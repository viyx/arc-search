import networkx as nx
import numpy as np
from networkx import DiGraph

from reprs.extractors import extract_bag, extract_region


def _get_maxdepth(g: DiGraph) -> int:
    # buggy
    return int(list(g.nodes)[-1][0])


def add_first_level(g: DiGraph, data: np.ndarray) -> None:
    g.add_node("1", data=data)
    for i, x in enumerate(data):
        hashes = {}
        r = extract_region(x, hashes, 0)
        g.add_node(f"2_{i}", data=r, hashes=hashes)
        g.add_edge("1", f"2_{i}", op="extract_region")


def add_next_level(g: DiGraph) -> None:
    maxl = _get_maxdepth(g)

    def _filter_node(n):
        return str(maxl) in n

    level_nodes = list(nx.subgraph_view(g, filter_node=_filter_node))
    for x in level_nodes:
        hashes = {}
        r = extract_bag(g.nodes[x]["data"].content, hashes, 0)
        name = str(int(x[0]) + 1) + x[0:]
        g.add_node(name, data=r, hashes=hashes)
        g.add_edge(x, name, op="extract_bag")
