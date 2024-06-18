import numpy as np
from networkx import DiGraph

from reprs.extractors import extract_bag, extract_region
from reprs.primitives import Bag
from search.lgg import lgg_prim


def _extract_regs(data, bg):
    bags = []
    hashes = {}
    for x in data:
        r = extract_region(x, hashes, bg=bg)
        b = Bag(regions=[r], length=1)
        bags.append(b)
    return bags, hashes


def _extract_bags(data, bg):
    hashes = {}
    bags = []
    for bag in data:
        for r in bag:
            r = extract_bag(r.content, hashes, bg)
            bags.append(r)
        bags.append(bags)
    return bags, hashes


def add_first_repr(
    g: DiGraph,
    data: np.ndarray,
    opname: str,
    parent: str,
    bg: int,
    test_data: np.ndarray | None = None,
) -> str:
    nname = f"{parent}_{opname}_{str(bg)}"
    bags, hashes = _extract_regs(data, bg)
    lgg = lgg_prim(bags)
    if test_data:
        test_bags, test_hashes = _extract_regs(test_data, bg)
        g.add_node(
            nname,
            lgg=lgg,
            data=bags,
            hashes=hashes,
            test_data=test_bags,
            test_hashes=test_hashes,
        )
    else:
        g.add_node(nname, lgg=lgg, data=bags, hashes=hashes)

    g.add_edge(parent, nname)
    return nname


def add_parameter_node(g: DiGraph, pname: str, parent: str) -> str:
    nname = parent + "_" + pname
    g.add_node(nname, type="parameter")
    g.add_edge(parent, nname)
    return nname


def add_repr(g: DiGraph, pname: str, parent: str, bg: int) -> str:
    nname = parent + "_" + pname
    data: list[Bag] = g.nodes[parent]["data"]
    bags, hashes = _extract_bags(data, bg)
    if "test_data" in g.nodes[parent]:
        test_data = g.nodes[parent]["test_data"]
        test_bags, test_hashes = _extract_bags(test_data, bg)
        g.add_node(
            nname,
            data=bags,
            hashes=hashes,
            test_data=test_bags,
            test_hashes=test_hashes,
        )
    else:
        g.add_node(nname, data=bags, hashes=hashes)
    g.add_edge(parent, nname)
    return nname
