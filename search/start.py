import logging
from collections import defaultdict
from itertools import product, zip_longest
from queue import PriorityQueue

import numpy as np

import search.actions as A
from datasets.arc import RawTaskData
from reprs.primitives import Bag, BBag, TaskBag
from search.distances import dict_keys_dist, dl
from search.graph import BiDag


class TaskSearch:
    def __init__(self, task: RawTaskData) -> None:
        self.logger = logging.getLogger("app.search")
        self.bt = BiDag()
        self.task = task
        self.success = False
        self.q = PriorityQueue()
        self.closed = set()
        self.xclosed: dict[str, A.ExtractAction] = defaultdict(set)
        self.yclosed: dict[str, A.ExtractAction] = defaultdict(set)
        self.opened = set()

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
        make_dump_regions = A.ExtractAction(name=A.Extractors.ER, c=1, bg=-1)
        self.bt.xdag.try_add_node(
            "0",
            parent="",
            bbag=BBag(bags=list(map(make_dump_regions, self.task.train_x))),
            test_data=BBag(bags=list(map(make_dump_regions, self.task.test_x))),
        )
        self.bt.ydag.try_add_node(
            "0",
            parent="",
            bbag=BBag(bags=list(map(make_dump_regions, self.task.train_y))),
            solved_yet={},
            solved=False,
        )
        self.put({"0"}, {"0"})

    def search_topdown(self) -> None:
        self._init_search()
        while self.q.qsize() != 0:
            self.logger.debug(
                "size(q, x, y) = (%s, %s, %s)",
                self.q.qsize(),
                self.bt.xdag.g.number_of_nodes(),
                self.bt.ydag.g.number_of_nodes(),
            )
            _, xnode, ynode = self._get()
            xclos, yclos = self.xclosed[xnode], self.yclosed[ynode]
            tbag = TaskBag.from_tuple(self.bt.get_bags(xnode, ynode, True))

            # solved_yet = self.bt.ydag.get_data_by_attr(ynode, "solved_yet")
            # ind1 = fast11_induction(xbags, ybags, solved_yet)
            # self.add_solved_yet(ynode, xnode, ind1)

            # if self.bt.ydag.get_data_by_attr(ynode, "solved"):
            #     self.success = True
            #     continue

            xposib_acts = A.possible_actions(tbag.x) - xclos
            yposib_acts = A.possible_actions(tbag.y) - yclos
            new_ynodes = set()
            new_xnodes = set()

            for xa, ya in zip_longest(xposib_acts, yposib_acts):
                if xa:
                    newx_bbag = BBag(bags=A.extract_flat(xa, tbag.x))
                    newxtest_bbag = BBag(bags=A.extract_flat(xa, tbag.test))
                    x_newname = self.bt.xdag.try_add_node(
                        xa, xnode, newx_bbag, test_data=newxtest_bbag, action=xa
                    )
                    if x_newname:
                        new_xnodes.add(x_newname)
                    self.xclosed[xnode].add(xa)
                if ya:
                    newy_bbag = BBag(bags=A.extract_flat(ya, tbag.y))
                    y_newname = self.bt.ydag.try_add_node(
                        ya, ynode, newy_bbag, solved=False, solved_yet={}, action=ya
                    )
                    if y_newname:
                        new_ynodes.add(y_newname)
                    self.yclosed[ynode].add(ya)

            self.closed.add(f"{xnode}:{ynode}")
            if len(new_xnodes | new_ynodes) != 0:
                self.put(
                    new_ynodes or self.bt.ydag.g.nodes,
                    new_xnodes or self.bt.xdag.g.nodes,
                )

    def put(self, ynodes: set[str], xnodes: set[str]) -> None:
        for xnode, ynode in product(xnodes, ynodes):
            xbbag, ybbag, _ = self.bt.get_bags(xnode, ynode)
            d = dl(xbbag.bags, ybbag.bags)
            self._put(xnode, ynode, d)
            self.logger.debug("put search node %s", (xnode, ynode, d))

    def add_solved_yet(self, ynode: str, refnode: str, to_add: dict) -> None:
        "Make sortof `left join` for two dicts with possible nested dicts."
        solved_yet = self.bt.ydag.get_data_by_attr(ynode, "solved_yet")
        for k, v in to_add.items():
            if k not in solved_yet:
                solved_yet[k] = {"op": v, "ref": refnode}
            elif isinstance(v, dict):
                for k2, v2 in v:
                    if k2 not in solved_yet[k]:
                        solved_yet[k][k2] = {"op": v2, "ref": refnode}
        solved = np.isclose(dict_keys_dist(Bag.blank(), solved_yet, ["raw"]), 0)
        self.bt.ydag.g.nodes[ynode]["solved"] = solved
        self.bt.ydag.g.nodes[ynode]["solved_yet"] = solved_yet
