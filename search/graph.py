import logging
from typing import Any

from networkx import DiGraph

from reprs.primitives import Bag
from search.actions import Action


class DAG:
    def __init__(self) -> None:
        self.g = DiGraph()
        self.logger = logging.getLogger("app.graph")

    def filter_by(self, attr: str, value: Any) -> list[str]:
        nodes = self.g.nodes.data(attr)
        return [k for k, v in nodes if v == value]

    def _get_values_upstream(self, node: str, attr: str) -> list[Any]:
        # assumed tree-like dag
        def _r(node: str, attr: str, res: list):
            res.append(self.get_data_by_attr(node, attr))
            preds = list(self.g.predecessors(node))
            if preds:
                if len(preds) > 1:
                    raise NotImplementedError()
                return _r(preds[0], attr, res)
            return res

        return _r(node, attr, [])

    def get_actions_upstream(self, node: str) -> list[Action]:
        return self._get_values_upstream(node, "action")

    def can_add_node(self, content_hash: str) -> bool:
        same_hash = self.filter_by("content_hash", content_hash)
        if len(same_hash) > 0:
            self.logger.debug("find duplicate hash %s", content_hash)
            if len(same_hash) > 1:
                raise KeyError(f"{len(same_hash)} nodes with the same content.")
            return False
        return True

    def try_add_node(
        self,
        action: Action,
        parent: str,
        bags: tuple[Bag],
        test_bags: tuple[Bag] | None,
        **kwargs,
    ) -> str | None:
        if any(b.is_empty() for b in bags) or (
            test_bags and any(b.is_empty() for b in test_bags)
        ):
            return None
        if self.can_add_node(
            content_hash := hash(str(hash(bags)) + str(hash(test_bags)))
        ):
            new_name = f"{parent} --> {action}" if parent else str(action)
            self.g.add_node(
                new_name,
                data=bags,
                test_data=test_bags,
                content_hash=content_hash,
                action=action,
                **kwargs,
            )
            self.logger.debug("add node %s", new_name)
            if parent:
                self.g.add_edge(parent, new_name)
            return new_name
        return None

    def get_data_by_attr(self, node: str, attr: str) -> Any:
        return self.g.nodes[node][attr]

    # def add_solved_yet(self, node: str, refnode: str, to_add: dict) -> None:
    #     "Make `left join` for two dicts with possible nested dicts."
    #     solved_yet = self.get_data_by_attr(node, "solved_yet")
    #     for k, v in to_add.items():
    #         if k not in solved_yet:
    #             solved_yet[k] = {"op": v, "ref": refnode}
    #         elif isinstance(v, dict):
    #             for k2, v2 in v:
    #                 if k2 not in solved_yet[k]:
    #                     solved_yet[k][k2] = {"op": v2, "ref": refnode}
    #     solved = np.isclose(dict_keys_dist(Region.blank(), solved_yet, ["raw"]), 0)
    #     self.g.nodes[node]["solved"] = solved
    #     self.g.nodes[node]["solved_yet"] = solved_yet


class BiDag:
    def __init__(self) -> None:
        self.xdag = DAG()
        self.ydag = DAG()

    def get_bags(
        self, xnode: str, ynode: str
    ) -> tuple[tuple[Bag], tuple[Bag], tuple[Bag], tuple[Bag] | None]:
        xbags = self.xdag.get_data_by_attr(xnode, "data")
        xtest_bags = self.xdag.get_data_by_attr(xnode, "test_data")
        ybags = self.ydag.get_data_by_attr(ynode, "data")
        ytest_bags = self.ydag.get_data_by_attr(ynode, "test_data")
        return xbags, ybags, xtest_bags, ytest_bags
