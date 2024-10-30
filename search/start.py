import logging
from collections import defaultdict
from collections.abc import Sequence
from itertools import product
from queue import PriorityQueue

import numpy as np

import search.actions as A
from datasets.arc import RawTaskData
from reprs.primitives import Bag, Region, TaskBags
from search.distances import dl
from search.graph import DAG
from search.solvers.pipeline import solve_pipe

INIT_ACTION = A.INIT_ACTIONS[0]


class TaskSearch:
    def __init__(self, task: RawTaskData) -> None:
        self.logger = logging.getLogger("app.search")
        self.load_testy = True  # ??
        self.xdag = DAG()
        self.ydag = DAG()
        self.task = task
        self.success = False
        self.q = PriorityQueue()
        self.closed = set()
        self.x_closed_acts: dict[str, set[A.Action]] = defaultdict(set)
        self.y_closed_acts: dict[str, set[A.Action]] = defaultdict(set)

    def _get(self) -> tuple[float, str, str, frozenset]:
        dist, x, y, exclude = self.q.get()
        self.logger.debug("get node %s", (dist, x, y, exclude))
        return dist, x, y, exclude

    def _put(
        self,
        xnodes: set[str],
        ynodes: set[str],
        *,
        exclude: frozenset[str],
        hard_dist: float | None = None
    ) -> None:
        if len(xnodes) > 0 and len(ynodes) > 0:
            new_pairs = set(product(xnodes, ynodes, [exclude]))
            new_pairs.discard(self.closed)
            for xnode, ynode, _ in new_pairs:
                # if xnode == "R(-1, 1) --> P( 0,-1)"
                # and ynode == "R(-1, 1) --> P( 0,-1)":
                #     hard_dist = -1
                xbags, ybags, *_ = self._get_bags(xnode, ynode)
                d = hard_dist or dl(xbags, ybags)
                self.q.put((d, xnode, ynode, exclude))
                self.logger.debug("put node %s", (d, xnode, ynode, exclude))

    def _init_search(self) -> None:
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
        self._put({xnode}, {ynode}, exclude=frozenset())

    def search_topdown(self) -> None:
        self._init_search()
        i = 0
        while self.q.qsize() != 0 and not self.success and i < 1000:
            i += 1
            self.logger.debug(
                "%s: size(q, x, y) = (%s, %s, %s)",
                i,
                self.q.qsize(),
                self.xdag.g.number_of_nodes(),
                self.ydag.g.number_of_nodes(),
            )
            _, xnode, ynode, exclude = self._get()
            tbag = TaskBags.from_tuples(
                *self.xdag.get_data(xnode), *self.ydag.get_data(ynode)
            )
            ans = solve_pipe(tbag, exclude=exclude)
            self.closed.add((xnode, ynode, exclude))
            if not ans:
                self._expand(tbag, xnode, ynode)
                continue

            self.ydag.set_solution(ynode, ans, tbag.collect_hashes())
            if ynode == self.ydag.init_node:
                self.success = True
                continue

            xparent = self.xdag.get_parent(xnode)
            yparent = self.ydag.get_parent(ynode)
            new_exclude = frozenset(Region.content_props())
            # if A.is_nobg_action(curr_act_y):
            # new_exclude.update({"width", "height"})
            # we can get width and height from successors
            # self._put({xparent}, {yparent}, , hard_dist=-1)
            self._put({xparent}, {yparent}, exclude=new_exclude, hard_dist=-1)
            # self.closed.add((xnode, ynode, exclude))

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

        # xnew_acts = A.next_actions(tbag.x, [], False) - xclos
        xnew_acts = A.next_actions(tbag.x, prev_acts_x, True) - xclos
        ynew_acts = A.next_actions(tbag.y, prev_acts_y, True) - yclos

        new_xnodes = self._add_nodes(self.xdag, xnew_acts, xnode, tbag.x, tbag.x_test)
        new_ynodes = self._add_nodes(self.ydag, ynew_acts, ynode, tbag.y, tbag.y_test)

        self.x_closed_acts[xnode].update(new_xnodes)
        self.y_closed_acts[ynode].update(new_ynodes)
        if len(new_xnodes | new_ynodes) > 0:
            xs_expand = new_xnodes or set(self.xdag.g.nodes)
            ys_expand = new_ynodes or set(self.ydag.g.nodes)
            self._put(xs_expand, ys_expand, exclude=frozenset())

    def _get_bags(
        self, xnode: str, ynode: str
    ) -> tuple[tuple[Bag], tuple[Bag], tuple[Bag], tuple[Bag] | None]:
        x, xtest = self.xdag.get_data(xnode)
        y, ytest = self.ydag.get_data(ynode)
        return x, y, xtest, ytest

    def test(self) -> list[np.ndarray] | None:
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
                prop = Region.content_props().pop()
                sample = si[0]
                for reg in si:
                    xs, ys = np.where(skeletons[i] == -1)
                    skeletons[i][xs, ys] = a.bg
                    if prop in sample:
                        cont: np.ndarray = hashes[reg[prop]]
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
