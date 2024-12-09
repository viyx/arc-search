from collections import defaultdict
from collections.abc import Sequence
from itertools import product
from queue import PriorityQueue

import numpy as np

import search.actions as A
from datasets.arc import RawTaskData
from log import AppLogger
from reprs.primitives import NO_BG, Bag, Region, TaskBags
from search.distances import edit_light
from search.graph import DAG
from search.solvers.pipeline import main_pipe

INIT_ACTION = A.INIT_ACTIONS[0]


class TaskSearch(AppLogger):
    """
    Implements a hybrid search algorithm combining A* and bidirectional search
    with support for iterative deepening in representations.

    Main fields:
    - `xdag`: Manages x's(input) representations.
    - `ydag`: Manages y's(output) representations.
    - `q`: Search priority queue with pairs from `xdag` and `ydag` nodes.
    - `closed`: Visited search nodes.
    - `x_closed_acts`: Actions which were already applyed to `xdag`'s representation.
    - `y_closed_acts`: Actions which were already applyed to `ydag`'s representation.

    Key Features:
    - Node Pairing: Pairs of nodes from `xdag` and `ydag` are added to a
      priority queue, with priority determined by the symbolic distance between
      their representations.
    - Iterative Deepening: The search explores the DAGs in a top-down
      manner, progressively deepening to lower levels of representations.
    - Bidirectional Search: Searches both input (`xdag`) and output (`ydag`)
      spaces simultaneously, attempting to synthesize a program that connects the two.
    - Timeout Handling: The search is successful if it synthesizes a program
      before the timeout is reached.
    - Prioritize of parent nodes that have solutions for children.
    """

    def __init__(self, parent_logger: str, task: RawTaskData) -> None:
        super().__init__(parent_logger)
        self.load_testy = True
        self.xdag = DAG(parent_logger=parent_logger)
        self.ydag = DAG(parent_logger=parent_logger)
        self.task = task
        self.success = False
        self._reset()

    def _reset(self) -> None:
        self.success = False
        self.q = PriorityQueue()
        self.closed = set()
        self.x_closed_acts: dict[str, set[A.Action]] = defaultdict(set)
        self.y_closed_acts: dict[str, set[A.Action]] = defaultdict(set)

    def _get(self) -> tuple[float, str, str, dict]:
        dist, x, y, kwargs = self.q.get()
        self.logger.debug("get node %s", (dist, x, y, kwargs))
        return dist, x, y, dict(kwargs)

    def _put(
        self,
        xnodes: set[str],
        ynodes: set[str],
        hard_dist: float | None = None,
        **kwargs,
    ) -> None:
        """Put crossproduct of nodes into search queue.
        Calculate distance value for each pair."""
        if len(xnodes) > 0 and len(ynodes) > 0:
            new_pairs = set(product(xnodes, ynodes, [frozenset(kwargs.items())]))
            new_pairs.discard(self.closed)
            for xnode, ynode, kwarg in new_pairs:
                xbags, ybags, *_ = self._get_bags(xnode, ynode)
                d = hard_dist or edit_light(xbags, ybags)
                # uncomment the hardcode to prioritize pixel
                # representations with black bg
                # if (
                #     xnode == "R(-1, 1) --> P( 0,-1)"
                #     and ynode == "R(-1, 1) --> P( 0,-1)"
                # ):
                #     d = -1
                self.q.put((d, xnode, ynode, kwarg))
                self.logger.debug("put node %s", (d, xnode, ynode, kwarg))

    def init(self) -> None:
        "Add init action for each graph."
        # TODO. Reset graph's content
        self._reset()
        make_dump_regions = INIT_ACTION
        xnode = self.xdag.try_add_node(
            make_dump_regions,
            parent=None,
            bags=tuple(map(make_dump_regions, self.task.train_x)),
            test_bags=tuple(map(make_dump_regions, self.task.test_x)),
        )
        ynode = self.ydag.try_add_node(
            make_dump_regions,
            parent=None,
            bags=tuple(map(make_dump_regions, self.task.train_y)),
            test_bags=tuple(map(make_dump_regions, self.task.test_y))
            if self.load_testy
            else None,
        )
        self._put({xnode}, {ynode})

    def search_topdown(self) -> None:
        i = 0
        while self.q.qsize() != 0 and not self.success and i < 1000:
            i += 1
            self.logger.info(
                "step %s: size(q, x, y) = (%s, %s, %s)",
                i,
                self.q.qsize(),
                self.xdag.g.number_of_nodes(),
                self.ydag.g.number_of_nodes(),
            )
            _, xnode, ynode, kwargs = self._get()
            tbag = TaskBags.from_tuples(
                *self.xdag.get_data(xnode), *self.ydag.get_data(ynode)
            )
            if not (ans := self.ydag.get_solution(ynode)):
                self.logger.info(
                    "starting pipe, xnode=%s, ynode=%s, kwargs=%s", xnode, ynode, kwargs
                )
                ans = main_pipe(self.parent_logger, tbag, **kwargs)
                if ans:
                    self.ydag.set_solution(ynode, ans, tbag.collect_hashes())
            self.closed.add((xnode, ynode, frozenset(kwargs.items())))
            if not ans:
                self._expand(tbag, xnode, ynode)
                continue

            if ynode == self.ydag.init_node:
                self.success = True
                continue

            # TODO. Need to recalcute all distances for solved ynode
            # after solution was found. Now try to solve parent nodes
            # using only size and positional features
            xparent = self.xdag.get_parent(xnode)
            yparent = self.ydag.get_parent(ynode)
            exclude = frozenset(Region.content_props())
            include = frozenset(Region.size_props())
            self._put(
                {xparent},
                {yparent},
                hard_dist=-1,
                exclude=exclude,
                include=include,
            )

    def _add_nodes(
        self,
        dag: DAG,
        actions: set[A.Action],
        parent: str,
        bags: Sequence[Bag],
        test_bags: Sequence[Bag] | None,
    ) -> set[str]:
        newnodes = set()
        for a in sorted(actions):
            new_bags = A.apply_forall(a, bags)
            newtest_bags = A.apply_forall(a, test_bags) if test_bags else None
            new_node = dag.try_add_node(a, parent, new_bags, newtest_bags)
            if new_node:
                newnodes.add(new_node)
        return newnodes

    def _expand(self, tbag: TaskBags, xnode: str, ynode: str) -> None:
        """Find possible actions, apply those actions and add new nodes into dags.
        After that, put the new nodes into search queue."""
        xclos, yclos = self.x_closed_acts[xnode], self.y_closed_acts[ynode]
        prev_acts_y = self.ydag.get_actions_upstream(ynode)
        prev_acts_x = self.xdag.get_actions_upstream(xnode)

        xnew_acts = A.next_actions(tbag.x, prev_acts_x, determinate=True) - xclos
        ynew_acts = A.next_actions(tbag.y, prev_acts_y, determinate=True) - yclos

        new_xnodes = self._add_nodes(self.xdag, xnew_acts, xnode, tbag.x, tbag.x_test)
        new_ynodes = self._add_nodes(self.ydag, ynew_acts, ynode, tbag.y, tbag.y_test)

        self.x_closed_acts[xnode].update(new_xnodes)
        self.y_closed_acts[ynode].update(new_ynodes)
        if len(new_xnodes | new_ynodes) > 0:
            # put all nodes if there are no new ones
            xs_expand = new_xnodes or set(self.xdag.g.nodes)
            ys_expand = new_ynodes or set(self.ydag.g.nodes)
            self._put(xs_expand, ys_expand)

    def _get_bags(
        self, xnode: str, ynode: str
    ) -> tuple[tuple[Bag], tuple[Bag], tuple[Bag], tuple[Bag] | None]:
        x, xtest = self.xdag.get_data(xnode)
        y, ytest = self.ydag.get_data(ynode)
        return x, y, xtest, ytest

    # prototype function, which can have bugs
    def test(self) -> list[np.ndarray] | None:
        """Create empty 30x30 grids and fill them with solutions' content,
        iteratively deepening."""
        if not self.success:
            return None
        # now it is assumed only one path is possible in the dag
        path = list(self.ydag.get_solved_down(self.ydag.init_node))
        path.insert(0, self.ydag.init_node)
        actions = self.ydag.get_actions(path)
        solutions = self.ydag.get_solutions(path)
        n = len(self.task.test_x)
        maxl, void_value = 30, -2
        grids = [np.full(shape=(maxl, maxl), fill_value=void_value) for _ in range(n)]
        for a, (s, hashes) in zip(actions, solutions):
            for i, si in enumerate(s):
                # assumed a single content property now
                cont_prop = Region.content_props().pop()
                # TODO. Coord-s can change with respect to a parent region
                xs, ys = np.where(grids[i] == NO_BG)
                grids[i][xs, ys] = a.bg
                for reg in si:
                    if cont_prop in reg:  # put data from saved hash.
                        # new NO_BG's can appear here
                        cont: np.ndarray = hashes[reg[cont_prop]]
                        height, width = cont.shape
                    else:  # put rectangle filled with bg
                        width, height = (reg[p] for p in Region.size_props())
                        cont = np.full(shape=(height, width), fill_value=a.bg)
                    x, y = [reg[p] for p in Region.position_props()]
                    grids[i][x : x + height, y : y + width] = cont
        # crop void
        for i in range(n):
            ybound = min(np.where(grids[i][0, :] == void_value)[0].tolist() or [maxl])
            xbound = min(np.where(grids[i][:, 0] == void_value)[0].tolist() or [maxl])
            grids[i] = grids[i][:xbound, :ybound]
        return grids
