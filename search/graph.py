from typing import Any, Generator

import networkx as nx
from networkx import DiGraph

from log import AppLogger
from reprs.primitives import Bag
from search.actions import Action

# TODO
# Add datatype/classes for solutions, nodes


class DAG(AppLogger):
    """A tree-like dag with some checkings of internal state.
    Mostly provides interface for data read/write operations."""

    def __init__(self, parent_logger: str) -> None:
        super().__init__(parent_logger)
        self.g = DiGraph()

    def _filter_nodes_by(self, attr: str, value: Any) -> set[str]:
        attrs = self.g.nodes.data(attr)
        return {k for k, v in attrs if v == value}

    def _get_values_upstream(self, node: str, attr: str) -> Generator[Any, None, None]:
        # while node:
        #     yield self._get_data_by_attr(node, attr)
        #     preds = list(self.g.predecessors(node))
        #     if len(preds) > 1:
        #         raise NotImplementedError("Found multiple parents for a node.")
        #     node = preds[0] if preds else None

        # TODO. Change recursion to Generator
        def _r(node: str, attr: str, res: list):
            res.append(self._get_data_by_attr(node, attr))
            preds = list(self.g.predecessors(node))
            if preds:
                if len(preds) > 1:
                    raise NotImplementedError("Found multiple parents for a node.")
                return _r(preds[0], attr, res)
            return res

        return _r(node, attr, [])

    def get_solved_down(self, node: str) -> Generator[str, None, None]:
        solved_nodes = set(self.g.nodes) - self._filter_nodes_by("sol", None)
        current_node = node

        while current_node:
            solved_children = solved_nodes & set(self.g.successors(current_node))
            if len(solved_children) > 1:
                raise NotImplementedError("Found multiple children with solutions.")
            current_node = solved_children.pop() if solved_children else None
            if current_node:
                yield current_node

    @property
    def init_node(self) -> str | None:
        return next(nx.topological_sort(self.g))

    def get_actions_upstream(self, node: str) -> list[Action]:
        return self._get_values_upstream(node, "action")

    def get_parent(self, node: str) -> str | None:
        preds = list(self.g.predecessors(node))
        if len(preds) > 1:
            raise NotImplementedError("Found multiple parents for a node.")
        if len(preds) == 0:
            return None
        return preds[0]

    def get_children(self, node: str) -> list[str]:
        return list(self.g.successors(node))

    def get_action(self, node: str) -> Action:
        return self._get_data_by_attr(node, "action")

    def get_solution(self, node: str) -> Any:
        return self._get_data_by_attr(node, "sol")

    def can_add_node(self, content_hash: str) -> bool:
        same_hash = self._filter_nodes_by("content_hash", content_hash)
        if len(same_hash) > 0:
            self.logger.debug("find duplicate hash %s", content_hash)
            if len(same_hash) > 1:
                raise KeyError(f"{len(same_hash)} nodes with the same content.")
            return False
        return True

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
            return None
        if self.can_add_node(
            content_hash := hash(str(hash(bags)) + str(hash(test_bags)))
        ):
            new_node = f"{parent} --> {action}" if parent else str(action)
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
        return None

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
