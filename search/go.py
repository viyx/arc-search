from collections import defaultdict
from collections.abc import Sequence
from itertools import product
from queue import PriorityQueue

import numpy as np

import search.actions as A
from datasets.arc import RawTaskData
from log import AppLogger
from reprs.primitives import NO_BG, Bag, Region, TaskBags
from search.distances import edit_like
from search.graph import DAG, split_to_actions
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
        self.task = task
        self.success = False
        self.q = PriorityQueue()
        self.closed = set()
        self.x_closed_acts: dict[str, set[A.Action]] = defaultdict(set)
        self.y_closed_acts: dict[str, set[A.Action]] = defaultdict(set)
        self.xdag = DAG(parent_logger=parent_logger)
        self.ydag = DAG(parent_logger=parent_logger)

    def _get(self) -> tuple[float, str, str, dict]:
        dist, x, y, kwargs = self.q.get()
        self.logger.debug("get node %s", (dist, x, y, kwargs))
        return dist, x, y, dict(kwargs)

    def _put(self, xnode: str, ynode: str, dist: float | None = None, **kwargs) -> None:
        if (xnode, ynode, frozenset(kwargs.items())) not in self.closed:
            if dist is None:
                xbags, _, ybags, _ = self._get_bags(xnode, ynode)
                dist = edit_like(xbags, ybags)
            search_node = (dist, xnode, ynode, frozenset(kwargs.items()))
            self.q.put(search_node)
            self.logger.debug("put node %s", search_node)
        else:
            self.logger.debug("skip adding a duplicate node %s", search_node)

    def _init(self) -> tuple[str, str]:
        "Add init action for each graph."
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
        return xnode, ynode

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

    # TODO. Check redundancy: can we get new actions after visiting a node?
    def _expand(self, tbag: TaskBags, xnode: str, ynode: str) -> None:
        """Find possible actions, apply these actions and add new nodes to the dags.
        Then put new nodes in the search queue."""
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
            self.put_crossproduct(xs_expand, ys_expand)

    def _get_bags(
        self, xnode: str, ynode: str
    ) -> tuple[tuple[Bag], tuple[Bag], tuple[Bag], tuple[Bag] | None]:
        x, xtest = self.xdag.get_data(xnode)
        y, ytest = self.ydag.get_data(ynode)
        return x, xtest, y, ytest

    def put_crossproduct(
        self, xnodes: set[str], ynodes: set[str], dist: float | None = None, **kwargs
    ) -> None:
        if len(xnodes) > 0 and len(ynodes) > 0:
            new_pairs = set(product(xnodes, ynodes, [frozenset(kwargs.items())]))
            new_pairs.discard(self.closed)
            for xnode, ynode, _ in new_pairs:
                if dist is None:
                    xbags, _, ybags, _ = self._get_bags(xnode, ynode)
                    dist = edit_like(xbags, ybags)
                self._put(xnode, ynode, dist, **kwargs)
        else:
            self.logger.debug("no nodes added")

    def reset(self) -> None:
        self.success = False
        self.q = PriorityQueue()
        self.closed = set()
        self.x_closed_acts: dict[str, set[A.Action]] = defaultdict(set)
        self.y_closed_acts: dict[str, set[A.Action]] = defaultdict(set)
        self.xdag = DAG(parent_logger=self.parent_logger)
        self.ydag = DAG(parent_logger=self.parent_logger)

    def search_topdown(self) -> None:
        if self.q.qsize() == 0:
            xinit, yinit = self._init()
            self._put(xinit, yinit)
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
            tbag = TaskBags.from_tuples(*self._get_bags(xnode, ynode))
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
                xparent,
                yparent,
                dist=-1,
                exclude=exclude,
                include=include,
            )

    # a prototype function that may have bugs
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

    def add_priority_nodes(self, xnode: str, ynode: str) -> None:
        # add the highest priority to the nodes
        if not self.xdag.g.number_of_nodes() == self.xdag.g.number_of_nodes() == 0:
            # temporary intergrity constaint
            raise NotImplementedError("Can only add nodes manually in empty dags.")
        xacts = list(map(A.Action.from_str, split_to_actions(xnode)))
        yacts = list(map(A.Action.from_str, split_to_actions(ynode)))
        if not xacts[0] == yacts[0] == INIT_ACTION:
            raise NotImplementedError("Can only start from init action.")
        xinit, yinit = self._init()
        xacts_rest, yacts_rest = xacts[1:], yacts[1:]  # skip one action after `init``
        groups = [(xinit, self.xdag, xacts_rest), (yinit, self.ydag, yacts_rest)]
        for node, dag, acts in groups:
            parent = node
            for a in acts:
                train, test = dag.get_data(parent)
                new_nodes = self._add_nodes(dag, {a}, parent, train, test)
                if not new_nodes:
                    raise RuntimeError("Can't add node.")
                parent = new_nodes.pop()
        self._put(xnode, ynode, dist=-1)
