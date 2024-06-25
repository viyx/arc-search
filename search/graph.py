import numpy as np
from networkx import DiGraph

from reprs.extractors import can_reduce_any, extract_bag, make_region
from reprs.primitives import Bag, Region
from search.distances import dict_keys_dist
from search.lgg import lgg_prim


def make_regions(data: list[np.ndarray], bg) -> tuple[list[Bag], list[dict]]:
    bags = []
    hashes = {}
    for x in data:
        r = make_region(x, hashes, bg=bg)
        b = Bag(regions=[r], length=1)
        bags.append(b)
    return bags, hashes


def extract_bags(data: list[np.ndarray], bg) -> tuple[list[Bag], list[dict]]:
    bags = []
    hashes = []
    for x in data:
        h = {}
        b = extract_bag(x, h, bg)
        bags.append(b)
        hashes.append(h)
    return bags, hashes


def add_td_1reg_repr(
    g: DiGraph,
    data: np.ndarray,
    opname: str,
    parent: str,
    bg: int,
    test_data: np.ndarray | None = None,
) -> str:
    nname = f"{parent}_{opname}_{str(bg)}"
    bags, hashes = make_regions(data, bg)
    level_lgg = lgg_prim(bags)
    if test_data:
        test_bags, test_hashes = make_regions(test_data, bg)
        g.add_node(
            nname,
            level_lgg=level_lgg,
            data=bags,
            hashes=hashes,
            test_data=test_bags,
            test_hashes=test_hashes,
        )
    else:
        g.add_node(nname, level_lgg=level_lgg, data=bags, hashes=hashes)

    g.add_edge(parent, nname)
    return nname


def add_topdown(
    g: DiGraph,
    data: list[np.ndarray],
    opname: str,
    parent: str,
    bg: int,
    test_data: list[np.ndarray] | None = None,
    **kwargs,
) -> str:
    nname = f"{parent}_{opname}_{str(bg)}"
    bags, hashes = extract_bags(data, bg)
    if "test_data" in g.nodes[parent]:
        test_bags, test_hashes = extract_bags(test_data, bg)
        g.add_node(
            nname,
            data=bags,
            hashes=hashes,
            test_data=test_bags,
            test_hashes=test_hashes,
        )
    else:
        g.add_node(nname, data=bags, hashes=hashes, **kwargs)
    g.add_edge(parent, nname)
    return nname


class BiTree:
    def __init__(self) -> None:
        self.gx = DiGraph()
        self.gy = DiGraph()

    def _get_same_x(self, data_hash: str) -> list[str]:
        hashes = self.gx.nodes.data("data_hash")
        return [k for k, v in hashes if v == data_hash]

    def _get_same_y(self, data_hash: str) -> list[str]:
        hashes = self.gy.nodes.data("data_hash")
        return [k for k, v in hashes if v == data_hash]

    def add_or_get_node_x(
        self,
        name: str,
        data: list[Bag],
        hashes: list[dict],
        test_data: list[Bag] | None = None,
        test_hashes: list[dict] | None = None,
    ) -> None:
        data_hash = str(
            hash(f"{[hash(b) for b in data]}_{[hash(b) for b in test_data]}")
        )
        sim = self._get_same_x(data_hash)
        if sim:
            if len(sim) > 1:
                raise LookupError()
            return sim[0]
        self.gx.add_node(
            name,
            data=data,
            test_data=test_data,
            hashes=hashes,
            test_hashes=test_hashes,
            data_hash=data_hash,
        )
        return name

    def add_or_get_node_y(self, name: str, data: list[Bag], hashes: list[dict]) -> None:
        data_hash = str(hash(str([hash(b) for b in data])))
        sim = self._get_same_y(data_hash)
        if sim:
            if len(sim) > 1:
                raise LookupError()
            return sim[0]
        self.gy.add_node(
            name,
            data=data,
            hashes=hashes,
            solved_yet={},
            solved=False,
            data_hash=data_hash,
        )
        return name

    def get_xdata(self, xnode: str) -> list[Bag]:
        if xnode not in self.gx.nodes:
            raise ValueError()
        return self.gx.nodes[xnode]["data"]

    def get_xtestdata(self, xnode: str) -> list[Bag]:
        if xnode not in self.gx.nodes:
            raise ValueError()
        return self.gx.nodes[xnode]["test_data"]

    def get_ydata(self, ynode: str) -> list[Bag]:
        if ynode not in self.gx.nodes:
            raise ValueError()
        return self.gy.nodes[ynode]["data"]

    def get_solved_yet(self, ynode: str) -> dict:
        if ynode not in self.gx.nodes:
            raise ValueError()
        return self.gy.nodes[ynode]["solved_yet"]

    def get_solved(self, ynode: str) -> bool:
        if ynode not in self.gx.nodes:
            raise ValueError()
        return self.gy.nodes[ynode]["solved"]

    def add_solved_yet(self, ynode: str, xnode: str, to_add: dict) -> None:
        "Make sortof `left join` for two dicts with possible nested dicts."
        if ynode not in self.gx.nodes or xnode not in self.gx:
            raise ValueError()
        solved_yet = self.get_solved_yet(ynode)
        for k, v in to_add.items():
            if k not in solved_yet:
                solved_yet[k] = {"op": v, "ref": xnode}
            elif isinstance(v, dict):
                for k2, v2 in v:
                    if k2 not in solved_yet[k]:
                        solved_yet[k][k2] = {"op": v2, "ref": xnode}
        solved = np.isclose(dict_keys_dist(Bag.blank(), solved_yet, ["raw"]), 0)
        self.gy.nodes[ynode]["solved"] = solved

    def get_flatten_regions_y(self, ynode: str) -> list[np.ndarray]:
        return [r.raw for b in self.get_ydata(ynode) for r in b.regions]

    def get_flatten_regions_x(self, xnode: str) -> list[Region]:
        return [r.raw for b in self.get_xdata(xnode) for r in b.regions]

    def get_flatten_regions_test(self, xnode: str) -> list[Region]:
        return [r.raw for b in self.get_xtestdata(xnode) for r in b.regions]

    def add_topdown_x(self, node: str, bg: int) -> str | None:
        data_test_flatten = self.get_flatten_regions_test(node)
        data_flatten = self.get_flatten_regions_x(node)
        if not can_reduce_any(data_flatten) and not can_reduce_any(data_test_flatten):
            return None
        bags, hashes = extract_bags(data_flatten, bg)
        test_bags, test_hashes = extract_bags(data_test_flatten, bg)
        candidate_name = f"{node}_TD_{bg}"
        newname = self.add_or_get_node_x(
            candidate_name,
            data=bags,
            hashes=hashes,
            test_hashes=test_hashes,
            test_data=test_bags,
        )
        self.gx.add_edge(node, newname)
        return newname

    def add_topdown_y(self, node: str, bg: int) -> str | None:
        data_flatten = self.get_flatten_regions_y(node)
        if not can_reduce_any(data_flatten):
            return None
        bags, hashes = extract_bags(data_flatten, bg)
        candidate_name = f"{node}_TD_{bg}"
        newname = self.add_or_get_node_y(candidate_name, data=bags, hashes=hashes)
        self.gy.add_edge(node, newname)
        return newname
