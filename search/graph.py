from typing import Any

import numpy as np
from networkx import DiGraph

from reprs.extractors import extract_bag, make_region
from reprs.primitives import Bag


def make_regions(data: list[np.ndarray], bg) -> tuple[list[Bag], list[dict]]:
    bags = []
    hashes = {}
    for x in data:
        r = make_region(x, 0, 0, hashes, bg)
        b = Bag(regions=[r], length=1)
        bags.append(b)
    return bags, hashes


def extract_bags(data: list[np.ndarray], c: int, bg: int) -> tuple[list[Bag], dict]:
    bags = []
    hashes = {}
    for x in data:
        h = {}
        b = extract_bag(x, h, c, bg)
        bags.append(b)
        hashes.update(h)
    return bags, hashes


def bags_hash(data: list[Bag]) -> str:
    content_hash = str(hash(f"{[hash(b) for b in data]}"))
    return content_hash


class DAG:
    def __init__(self) -> None:
        self.g = DiGraph()

    def filter_by(self, attr: str, value: Any) -> list[str]:
        nodes = self.g.nodes.data(attr)
        return [k for k, v in nodes if v == value]

    def can_add_node(self, bags: list[Bag]) -> bool:
        content_hash = bags_hash(bags)
        same_hash = self.filter_by("content_hash", content_hash)
        lngh = len(same_hash)
        if lngh > 0:
            if lngh > 1:
                raise KeyError(f"{lngh} nodes with the same content.")
            return False
        return True

    def add_node(
        self, name: str, data: list[Bag], hashes: list[dict], **kwargs
    ) -> None:
        if self.can_add_node(data):
            content_hash = bags_hash(data)
            self.g.add_node(
                name, data=data, hashes=hashes, content_hash=content_hash, **kwargs
            )

    def get_data_by(self, node: str, attr: str) -> list[Any]:
        return self.g.nodes[node][attr]


class BiDAG:
    def __init__(self) -> None:
        self.xdag = DAG()
        self.ydag = DAG()

    # def _get_same_x(self, data_hash: str) -> list[str]:
    #     hashes = self.gx.nodes.data("data_hash")
    #     return [k for k, v in hashes if v == data_hash]

    # def _get_same_y(self, data_hash: str) -> list[str]:
    #     hashes = self.gy.nodes.data("data_hash")
    #     return [k for k, v in hashes if v == data_hash]

    # def add_node_x(
    #     self,
    #     name: str,
    #     data: list[Bag],
    #     hashes: list[dict],
    #     test_data: list[Bag],
    #     test_hashes: list[dict],
    # ) -> None:
    #     data_hash = str(
    #         hash(f"{[hash(b) for b in data]}_{[hash(b) for b in test_data]}")
    #     )
    #     self.gx.add_node(
    #         name,
    #         data=data,
    #         test_data=test_data,
    #         hashes=hashes,
    #         test_hashes=test_hashes,
    #         data_hash=data_hash,
    #     )

    # def add_node_y(self, name: str, data: list[Bag], hashes: list[dict]) -> None:
    #     data_hash = str(hash(str([hash(b) for b in data])))
    #     self.gy.add_node(
    #         name,
    #         data=data,
    #         hashes=hashes,
    #         solved_yet={},
    #         solved=False,
    #         data_hash=data_hash,
    #     )

    # def get_xdata(self, xnode: str) -> list[Bag]:
    #     if xnode not in self.gx.nodes:
    #         raise ValueError()
    #     return self.gx.nodes[xnode]["data"]

    # def get_xtestdata(self, xnode: str) -> list[Bag]:
    #     if xnode not in self.gx.nodes:
    #         raise ValueError()
    #     return self.gx.nodes[xnode]["test_data"]

    # def get_ydata(self, ynode: str) -> list[Bag]:
    #     if ynode not in self.gy.nodes:
    #         raise ValueError()
    #     return self.gy.nodes[ynode]["data"]

    # def get_solved_yet(self, ynode: str) -> dict:
    # if ynode not in self.gy.nodes:
    #     raise ValueError()
    # return self.gy.nodes[ynode]["solved_yet"]

    # def is_solved(self, ynode: str) -> bool:
    #     if ynode not in self.gy.nodes:
    #         raise ValueError()
    #     return self.gy.nodes[ynode]["solved"]

    # def add_solved_yet(self, ynode: str, refnode: str, to_add: dict) -> None:
    #     "Make sortof `left join` for two dicts with possible nested dicts."
    #     if ynode not in self.gy.nodes or refnode not in self.gx:
    #         raise ValueError()
    #     solved_yet = self.get_solved_yet(ynode)
    #     for k, v in to_add.items():
    #         if k not in solved_yet:
    #             solved_yet[k] = {"op": v, "ref": refnode}
    #         elif isinstance(v, dict):
    #             for k2, v2 in v:
    #                 if k2 not in solved_yet[k]:
    #                     solved_yet[k][k2] = {"op": v2, "ref": refnode}
    #     solved = np.isclose(dict_keys_dist(Bag.blank(), solved_yet, ["raw"]), 0)
    #     self.gy.nodes[ynode]["solved"] = solved

    # def get_flatten_regions_y(self, ynode: str) -> list[np.ndarray]:
    #     return [r.raw for b in self.get_ydata(ynode) for r in b.regions]

    # def get_flatten_regions_x(self, xnode: str) -> list[Region]:
    #     return [r.raw for b in self.get_xdata(xnode) for r in b.regions]

    # def get_flatten_regions_test(self, xnode: str) -> list[Region]:
    # return [r.raw for b in self.get_xtestdata(xnode) for r in b.regions]

    def add_topdown_x(self, parent_node: str, c: int, bg: int) -> str | None:
        ebags: list[Bag] = self.xdag.get_data_by(parent_node, "data")
        ebags_test: list[Bag] = self.xdag.get_data_by(parent_node, "test_data")
        eregions: list[list[np.ndarray]] = [[r.raw for r in e.regions] for e in ebags]
        eregions_test: list[list[np.ndarray]] = [
            [r.raw for r in e.regions] for e in ebags_test
        ]

        node_bags = []  # per example bag
        node_hashes = []  # per example hashes
        for e in eregions:
            _ebags, _ehashes = extract_bags(e, c, bg)
            bag = Bag.merge(_ebags)
            node_bags.append(bag)
            node_hashes.append(_ehashes)

        node_bags_test = []
        node_hashes_test = []
        for e in eregions_test:
            _ebags, _ehashes = extract_bags(e, c, bg)
            bag = Bag.merge(_ebags)
            node_bags_test.append(bag)
            node_hashes_test.append(_ehashes)

        if self.xdag.can_add_node(node_bags):
            candidate_name = f"{parent_node}_TD_c={c}_b={bg}|"
            self.xdag.add_node(
                candidate_name,
                data=node_bags,
                hashes=node_hashes,
                test_hashes=node_hashes_test,
                test_data=node_bags_test,
            )
            self.xdag.g.add_edge(parent_node, candidate_name)
            return candidate_name
        return None

    def add_topdown_y(self, parent_node: str, c: int, bg: int) -> str | None:
        ebags: list[Bag] = self.ydag.get_data_by(parent_node, "data")
        eregions: list[list[np.ndarray]] = [[r.raw for r in e.regions] for e in ebags]

        node_bags = []  # per example bag
        node_hashes = []  # per example hashes
        for e in eregions:
            _ebags, _ehashes = extract_bags(e, c, bg)
            bag = Bag.merge(_ebags)
            node_bags.append(bag)
            node_hashes.append(_ehashes)
        if self.ydag.can_add_node(node_bags):
            candidate_name = f"{parent_node}_TD_c={c}_b={bg}|"
            self.ydag.add_node(
                candidate_name,
                data=node_bags,
                hashes=node_hashes,
                solved=False,
                solved_yet={},
            )
            self.ydag.g.add_edge(parent_node, candidate_name)
            return candidate_name
        return None
