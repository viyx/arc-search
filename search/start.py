import logging
from collections import defaultdict
from itertools import product, zip_longest
from queue import PriorityQueue

import search.actions as A
from datasets.arc import RawTaskData
from reprs.primitives import TaskBags
from search.distances import dl
from search.graph import BiDag
from search.inductions import exec_meta


class TaskSearch:
    def __init__(self, task: RawTaskData) -> None:
        self.logger = logging.getLogger("app.search")
        self.load_testy = True  # check in self.task
        self.bd = BiDag()
        self.task = task
        self.success = False
        self.q = PriorityQueue()
        self.closed = set()
        self.opened = set()
        self.xclosed: dict[str, A.Action] = defaultdict(set)
        self.yclosed: dict[str, A.Action] = defaultdict(set)

    def _put(self, xnode: str, ynode: str, dist: float) -> None:
        pair = f"{xnode}:{ynode}"
        t = (dist, pair)
        if pair not in (self.closed | self.opened):
            self.q.put(t)
            self.opened.add(pair)

    def _get(self) -> tuple[float, str, str]:
        dist, pair = self.q.get()
        self.logger.debug("get search node %s", (dist, pair))
        return dist, *pair.split(":")

    def _init_search(self) -> None:
        make_dump_regions = list(A.INIT_ACTIONS)[0]
        xnode = self.bd.xdag.try_add_node(
            make_dump_regions,
            parent="",
            bags=tuple(map(make_dump_regions, self.task.train_x)),
            test_bags=tuple(map(make_dump_regions, self.task.test_x)),
        )
        ynode = self.bd.ydag.try_add_node(
            make_dump_regions,
            parent="",
            bags=tuple(map(make_dump_regions, self.task.train_y)),
            test_bags=tuple(map(make_dump_regions, self.task.test_y))
            if self.load_testy
            else None,
            # sofar=Answer(Region.main_props()),
        )
        self.put({xnode}, {ynode})

    def search_topdown(self) -> None:
        self._init_search()
        while self.q.qsize() != 0 or self.success:
            self.logger.debug(
                "size(q, x, y) = (%s, %s, %s)",
                self.q.qsize(),
                self.bd.xdag.g.number_of_nodes(),
                self.bd.ydag.g.number_of_nodes(),
            )
            _, xnode, ynode = self._get()
            tbag = TaskBags.from_tuple(*self.bd.get_bags(xnode, ynode))
            # answer = self.bd.ydag.get_data_by_attr(ynode, "sofar")

            exec_meta(tbag, None)

            xclos, yclos = self.xclosed[xnode], self.yclosed[ynode]
            xposib_acts = A.next_actions(tbag.x) - xclos
            yposib_acts = A.next_actions(tbag.y) - yclos
            prev_acts = self.bd.ydag.get_actions_upstream(ynode)
            if yposib_acts and any(a.bg != -1 for a in prev_acts):
                yposib_acts = A.exclude_nobg_actions(yposib_acts)
            new_ynodes = set()
            new_xnodes = set()

            for xa, ya in zip_longest(xposib_acts, yposib_acts):
                if xa:
                    newx_bags = A.extract_flat(xa, tbag.x)
                    newxtest_bags = A.extract_flat(xa, tbag.x_test)
                    x_newname = self.bd.xdag.try_add_node(
                        xa, xnode, newx_bags, newxtest_bags
                    )
                    if x_newname:
                        new_xnodes.add(x_newname)
                    self.xclosed[xnode].add(xa)
                if ya:
                    newy_bags = A.extract_flat(ya, tbag.y)
                    newytest_bags = (
                        A.extract_flat(ya, tbag.y_test) if self.load_testy else None
                    )
                    y_newname = self.bd.ydag.try_add_node(
                        ya,
                        ynode,
                        newy_bags,
                        newytest_bags,
                        # sofar=Answer(Region.main_props()),
                    )
                    if y_newname:
                        new_ynodes.add(y_newname)
                    self.yclosed[ynode].add(ya)

            self.closed.add(f"{xnode}:{ynode}")
            if len(new_xnodes | new_ynodes) != 0:
                self.put(
                    new_xnodes or self.bd.xdag.g.nodes,
                    new_ynodes or self.bd.ydag.g.nodes,
                )
        pass

    def put(self, xnodes: set[str], ynodes: set[str]) -> None:
        for xnode, ynode in product(xnodes, ynodes):
            xbags, ybags, *_ = self.bd.get_bags(xnode, ynode)
            d = dl(xbags, ybags)
            self._put(xnode, ynode, d)
            self.logger.debug("put search node %s", (xnode, ynode, d))
