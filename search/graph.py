from typing import Any, Generator

import networkx as nx
from networkx import DiGraph

from log import AppLogger
from reprs.primitives import Bag
from search.actions import Action

SPLITTER = ">"


def name_node(parent: str | None, node: str) -> str:
    if parent:
        return f"{parent}{SPLITTER}{node}"
    return node


def split_to_actions(name: str) -> list[str]:
    return list(map(str.strip, name.split(SPLITTER)))


def actions_to_name(acts: list[Action]) -> str:
    name = ""
    parent = None
    for a in acts:
        name = name_node(parent, str(a))
        parent = str(a)
    return name


# TODO. Replace exceptions with integrity contraints when adding a node
class DAG(AppLogger):
    """A tree-like dag with some checkings of internal state.
    Mostly provides interface for data read/write operations.

    Note: Names of nodes are sequencies of actions in textual formats.
    Example, `Reg(-1, 1)>Prim( 0,-1)` defines the sequence of actions:
    1. extract_regions(bg=-1, connectivity=1)
    2. extract_primitives(bg=0, connectivity=-1)
    """

    def __init__(self, parent_logger: str) -> None:
        super().__init__(parent_logger)
        self.g = DiGraph()

    def _filter_nodes_by(self, attr: str, value: Any) -> set[str]:
        attrs = self.g.nodes.data(attr)
        return {k for k, v in attrs if v == value}

    def _get_values_upstream(self, node: str, attr: str) -> Generator[Any, None, None]:
        while node:
            yield self._get_data_by_attr(node, attr)
            preds = list(self.g.predecessors(node))
            if len(preds) > 1:
                raise NotImplementedError("Found multiple parents for a node.")
            node = preds[0] if preds else None

    def get_solved_down(self, node: str) -> Generator[str, None, None]:
        solved_nodes = set(self.g.nodes) - self._filter_nodes_by("sol", None)
        current_node = node

        while current_node:
            solved_childs = solved_nodes & set(self.g.successors(current_node))
            if len(solved_childs) > 1:
                raise NotImplementedError("Found multiple childs with solutions.")
            current_node = solved_childs.pop() if solved_childs else None
            if current_node:
                yield current_node

    @property
    def init_node(self) -> str | None:
        return next(nx.topological_sort(self.g))

    def get_actions_upstream(self, node: str) -> list[Action]:
        return list(self._get_values_upstream(node, "action"))

    def get_parent(self, node: str) -> str | None:
        preds = list(self.g.predecessors(node))
        if len(preds) > 1:
            raise NotImplementedError("Found multiple parents for a node.")
        if len(preds) == 0:
            return None
        return preds[0]

    def get_childs(self, node: str) -> list[str]:
        return list(self.g.successors(node))

    def get_action(self, node: str) -> Action:
        return self._get_data_by_attr(node, "action")

    def get_solution(self, node: str) -> Any:
        return self._get_data_by_attr(node, "sol")

    def set_solution(self, node: str, sol: Any, hashes: dict) -> None:
        prev_sol = self._get_data_by_attr(node, "sol")
        if prev_sol is not None:
            raise NotImplementedError("Unable to add solution to existing one.")
        self.g.nodes[node]["sol"] = (sol, hashes)

    def try_add_node(
        self,
        action: Action,
        parent: str | None,
        bags: tuple[Bag],
        test_bags: tuple[Bag] | None,
        sol: Any | None = None,
    ) -> str | None:
        if any(b.is_empty() for b in bags) or (
            test_bags and any(b.is_empty() for b in test_bags)
        ):
            self.logger.debug("cannot add empty bags")
            return None

        content_hash = hash(str(hash(bags)) + str(hash(test_bags)))
        same_nodes = self._filter_nodes_by("content_hash", content_hash)
        if len(same_nodes) > 0:
            self.logger.debug("find duplicate hash %s", content_hash)
            if len(same_nodes) > 1:
                raise RuntimeError(f"{len(same_nodes)} nodes with the same content.")
            return None
        new_node = name_node(parent, str(action))
        self.g.add_node(
            new_node,
            data=bags,
            test_data=test_bags,
            content_hash=content_hash,
            action=action,
            sol=sol,
        )
        self.logger.debug("add node %s", new_node)
        if parent:
            self.g.add_edge(parent, new_node)
        return new_node

    def _get_data_by_attr(self, node: str, attr: str) -> Any:
        return self.g.nodes[node][attr]

    def get_actions(self, nodes: list[str]) -> list[Action]:
        return [self._get_data_by_attr(n, "action") for n in nodes]

    def get_solutions(self, nodes: list[str]) -> list[Any]:
        return [self._get_data_by_attr(n, "sol") for n in nodes]

    def get_data(self, node: str) -> tuple[tuple[Bag], tuple[Bag] | None]:
        bags = self._get_data_by_attr(node, "data")
        test_bags = self._get_data_by_attr(node, "test_data")
        return bags, test_bags
