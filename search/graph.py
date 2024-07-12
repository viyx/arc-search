from typing import Any

import numpy as np
from networkx import DiGraph

from reprs.extractors import extract_bag, make_region
from reprs.primitives import Bag


def make_dump_regions(data: list[np.ndarray]) -> tuple[list[Bag], list[dict]]:
    bags = []
    hashes = {}
    for x in data:
        r = make_region(x, np.ones_like(x), 0, 0, hashes)
        b = Bag(regions=[r], length=1)
        bags.append(b)
    return bags, hashes


def extract_bags(data: list[np.ndarray], c: int, bg: int) -> tuple[list[Bag], dict]:
    bags = []
    hashes = {}
    for x in data:
        h = {}
        b = extract_bag(x, h, c, bg)
        if len(b.regions) > 0:
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

    def get_data_by_attr(self, node: str, attr: str) -> list[Any]:
        return self.g.nodes[node][attr]


class BiDAG:
    def __init__(self) -> None:
        self.xdag = DAG()
        self.ydag = DAG()

    def add_topdown_x(self, parent_node: str, c: int, bg: int) -> str | None:
        ebags: list[Bag] = self.xdag.get_data_by_attr(parent_node, "data")
        ebags_test: list[Bag] = self.xdag.get_data_by_attr(parent_node, "test_data")
        eregions: list[list[np.ndarray]] = [
            [r.raw_view for r in e.regions] for e in ebags
        ]
        eregions_test: list[list[np.ndarray]] = [
            [r.raw_view for r in e.regions] for e in ebags_test
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
        ebags: list[Bag] = self.ydag.get_data_by_attr(parent_node, "data")
        eregions: list[list[np.ndarray]] = [
            [r.raw_view for r in e.regions] for e in ebags
        ]

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
