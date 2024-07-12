from itertools import product
from queue import PriorityQueue

import numpy as np

from datasets.arc import RawTaskData
from reprs.primitives import Bag
from search.distances import dict_keys_dist, pairwise_dists
from search.graph import BiDAG, make_dump_regions
from search.inductions import fast11_induction
from search.lgg import lgg_prim


class TaskSearch:
    def __init__(self, task: RawTaskData) -> None:
        self.task = task
        self.success = False
        self.q = PriorityQueue()
        self.closed = set()
        self.opened = set()
        self.bt = BiDAG()

    def _put(self, xnode: str, ynode: str, dist: float) -> None:
        pair = f"{xnode}:{ynode}"
        t = (dist, pair)
        if pair not in (self.closed | self.opened):
            self.q.put(t)
            self.opened.add(pair)

    def _get(self) -> tuple[float, str, str]:
        dist, pair = self.q.get()
        return dist, *pair.split(":")

    def _init_search(self) -> None:
        x_bags, x_hashes = make_dump_regions(self.task.train_x)
        x_test_bags, x_test_hashes = make_dump_regions(self.task.test_x)
        y_bags, y_hashes = make_dump_regions(self.task.train_y)
        self.bt.xdag.add_node(
            "0",
            data=x_bags,
            hashes=x_hashes,
            test_data=x_test_bags,
            test_hashes=x_test_hashes,
        )
        self.bt.ydag.add_node(
            "0", data=y_bags, hashes=y_hashes, solved_yet={}, solved=False
        )
        self._put("0", "0", 0)

    def search_topdown(self) -> None:
        self._init_search()
        stop = False
        while self.q.qsize() != 0:
            _, xnode, ynode = self._get()

            xbags = self.bt.xdag.get_data_by_attr(xnode, "data")
            ybags = self.bt.ydag.get_data_by_attr(ynode, "data")

            solved_yet = self.bt.ydag.get_data_by_attr(ynode, "solved_yet")
            ind1 = fast11_induction(xbags, ybags, solved_yet)
            ind1 = {}

            self.add_solved_yet(ynode, xnode, ind1)
            if self.bt.ydag.get_data_by_attr(ynode, "solved"):
                self.success = True
                continue

            new_ynodes = set()
            new_xnodes = set()
            if not stop:
                for c, bg in product([1, 2], [-1, 0]):
                    xnew = self.bt.add_topdown_x(xnode, c, bg)
                    ynew = self.bt.add_topdown_y(ynode, c, bg)
                    if xnew:
                        new_xnodes.add(xnew)
                    if ynew:
                        new_ynodes.add(ynew)
                    stop = False

            self.closed.add(f"{xnode}:{ynode}")
            if len(new_xnodes | new_ynodes) != 0:
                self.put(
                    new_ynodes or self.bt.ydag.g.nodes,
                    new_xnodes or self.bt.xdag.g.nodes,
                )

    def put(self, ynodes: set[str], xnodes: set[str]) -> None:
        if len(ynodes) == len(xnodes) == 0:
            return
        x_lggs = [lgg_prim(self.bt.xdag.get_data_by_attr(n, "data")) for n in xnodes]
        y_lggs = [lgg_prim(self.bt.ydag.get_data_by_attr(n, "data")) for n in ynodes]

        dists = np.ravel(pairwise_dists(x_lggs, y_lggs))
        pairs = list(product(xnodes, ynodes))
        for d, (xnode, ynode) in zip(dists, pairs):
            self._put(xnode, ynode, d)

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
