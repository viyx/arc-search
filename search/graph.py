import logging
from typing import Any

from networkx import DiGraph

from reprs.primitives import BBag


class DAG:
    def __init__(self) -> None:
        self.g = DiGraph()
        self.logger = logging.getLogger("app.graph")

    def filter_by(self, attr: str, value: Any) -> list[str]:
        nodes = self.g.nodes.data(attr)
        return [k for k, v in nodes if v == value]

    # def recursive_get(self, node: str, attr: str) -> list[Any]:
    #     def _r(node: str, attr: str, res: list):
    #         res.append(self.get_data_by_attr(node, attr))
    #         preds = self.g.pred[node]
    #         if preds:
    #             if len(preds) > 1:
    #                 raise NotImplementedError()
    #             return _r(preds[0], attr, res)
    #         return res

    #     return _r(node, attr, [])

    def can_add_node(self, content_hash: str) -> bool:
        same_hash = self.filter_by("content_hash", content_hash)
        if len(same_hash) > 0:
            self.logger.debug("find duplicate hash %s", content_hash)
            if len(same_hash) > 1:
                raise KeyError(f"{len(same_hash)} nodes with the same content.")
            return False
        return True

    def try_add_node(self, name: str, parent: str, bbag: BBag, **kwargs) -> str | None:
        if self.can_add_node(content_hash := hash(bbag)):
            new_name = f"{parent}-->{name}" if parent else name
            self.g.add_node(new_name, data=bbag, content_hash=content_hash, **kwargs)
            self.logger.debug("add node %s", new_name)
            if parent:
                self.g.add_edge(parent, new_name)
            return new_name
        return None

    def get_data_by_attr(self, node: str, attr: str) -> Any:
        return self.g.nodes[node][attr]


class BiDag:
    def __init__(self) -> None:
        self.xdag = DAG()
        self.ydag = DAG()

    def get_bags(
        self, xnode: str, ynode: str, include_test: bool = False
    ) -> tuple[BBag, BBag, BBag | None]:
        xbbag = self.xdag.get_data_by_attr(xnode, "data")
        xtest_bbag = (
            self.xdag.get_data_by_attr(xnode, "test_data") if include_test else None
        )
        ybbag = self.ydag.get_data_by_attr(ynode, "data")
        return xbbag, ybbag, xtest_bbag

    # def get_path_attrs(
    #     self, xnode: str, ynode: str, attr: str
    # ) -> tuple[list[Any], list[Any]]:
    #     xhist = self.xdag.recursive_get(xnode, attr)
    #     yhist = self.ydag.recursive_get(ynode, attr)
    #     return xhist, yhist
