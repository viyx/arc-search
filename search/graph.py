import numpy as np
from networkx import DiGraph

from reprs.extractors import extract_bag, make_region
from reprs.primitives import Bag
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


def get_lggs(g: DiGraph, nodes: list[str]) -> list[dict]:
    return [g.nodes[n]["level_lgg"] for n in nodes]


def get_all_lggs(g: DiGraph) -> tuple[list[str], list[dict]]:
    names, lggs = [], []
    for n in g.nodes:
        if "level_lgg" in g.nodes[n]:
            names.append(n)
            lggs.append(g.nodes[n]["level_lgg"])
    return names, lggs
