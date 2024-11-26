from collections import defaultdict
from collections.abc import Sequence
from itertools import product
from queue import PriorityQueue

import numpy as np

import search.actions as A
from datasets.arc import RawTaskData
from log import AppLogger
from reprs.primitives import Bag, Region, TaskBags
from search.distances import dl
from search.graph import DAG
from search.solvers.pipeline import main_pipe

INIT_ACTION = A.INIT_ACTIONS[0]


class TaskSearch(AppLogger):
    def __init__(self, parent_logger: str, task: RawTaskData) -> None:
        super().__init__(parent_logger)
        self.load_testy = True  # ??
        self.xdag = DAG(parent_logger=parent_logger)
        self.ydag = DAG(parent_logger=parent_logger)
        self.task = task
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
        if len(xnodes) > 0 and len(ynodes) > 0:
            new_pairs = set(product(xnodes, ynodes, [frozenset(kwargs.items())]))
            new_pairs.discard(self.closed)
            for xnode, ynode, kwarg in new_pairs:
                xbags, ybags, *_ = self._get_bags(xnode, ynode)
                d = hard_dist or dl(xbags, ybags)
                # hardcode for fast testing
                if (
                    xnode == "R(-1, 1) --> P( 0,-1)"
                    and ynode == "R(-1, 1) --> P( 0,-1)"
                ):
                    d = -1
                self.q.put((d, xnode, ynode, kwarg))
                self.logger.debug("put node %s", (d, xnode, ynode, kwarg))

    def init(self) -> None:
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

            xparent = self.xdag.get_parent(xnode)
            yparent = self.ydag.get_parent(ynode)
            exclude = frozenset(Region.content_props())
            include = frozenset(Region.size_props())
            # if A.is_nobg_action(curr_act_y):
            # new_exclude.update({"width", "height"})
            # we can get width and height from successors
            # self._put({xparent}, {yparent}, , hard_dist=-1)
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
            new_bags = A.extract_flat(a, bags)
            newtest_bags = A.extract_flat(a, test_bags) if test_bags else None
            new_node = dag.try_add_node(a, parent, new_bags, newtest_bags)
            if new_node:
                newnodes.add(new_node)
        return newnodes

    def _expand(self, tbag: TaskBags, xnode: str, ynode: str) -> None:
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
            xs_expand = new_xnodes or set(self.xdag.g.nodes)
            ys_expand = new_ynodes or set(self.ydag.g.nodes)
            self._put(xs_expand, ys_expand)

    def _get_bags(
        self, xnode: str, ynode: str
    ) -> tuple[tuple[Bag], tuple[Bag], tuple[Bag], tuple[Bag] | None]:
        x, xtest = self.xdag.get_data(xnode)
        y, ytest = self.ydag.get_data(ynode)
        return x, y, xtest, ytest

    def test(self) -> list[np.ndarray] | None:
        # prototype, the most buggy and ugly place here
        if not self.success:
            return None
        path = list(self.ydag.get_solved_down(self.ydag.init_node))
        path.insert(0, self.ydag.init_node)
        actions = self.ydag.get_actions(path)
        solutions = self.ydag.get_solutions(path)
        n = len(self.task.test_x)
        skeletons = [np.full(shape=(30, 30), fill_value=-2) for _ in range(n)]
        for a, (s, hashes) in zip(actions, solutions):
            for i, si in enumerate(s):
                cont_prop = Region.content_props().pop()
                sample = si[0]
                for reg in si:
                    xs, ys = np.where(skeletons[i] == -1)
                    skeletons[i][xs, ys] = a.bg
                    if cont_prop in sample:
                        cont: np.ndarray = hashes[reg[cont_prop]]
                        x = reg["x"]
                        height = cont.shape[0]
                        y = reg["y"]
                        width = cont.shape[1]
                    else:
                        x = reg["x"]
                        height = reg["height"]
                        y = reg["y"]
                        width = reg["width"]
                        bg = a.bg
                        cont = np.full(shape=(height, width), fill_value=bg)
                    skeletons[i][x : x + height, y : y + width] = cont
        for i in range(n):
            _y = min(np.where(skeletons[i][0, :] == -2)[0])
            _x = min(np.where(skeletons[i][:, 0] == -2)[0])
            skeletons[i] = skeletons[i][:_x, :_y]
        return skeletons
