from abc import abstractmethod
from collections.abc import Sequence
from copy import copy
from typing import TypeVar

# import search.lgg as lgg
from log import AppLogger
from reprs.primitives import Bag, TaskBags
from search import lgg
from search.solvers.metafeatures import TaskMetaFeatures

LLD = list[list[dict]]

# class LabelEncoder:
#     def __init__(self):
#         self._state = 0
#         self._mapper = {}

#     def _add_item(self, value: Hashable) -> None:
#         if value not in self._mapper:
#             self._state += 1
#             self._mapper[value] = f"'{self._state}'"

#     def fit(self, data: Iterable[str]):
#         for d in data:
#             self._add_item(d)

#     def transform(self, key: Hashable) -> str:
#         if key not in self._mapper:
#             self._add_item(key)
#         return self._mapper[key]

#     def values(self) -> set[str]:
#         return set(self._mapper.values())

T = TypeVar("T", Bag, dict)
SSA = Sequence[Sequence[T]]
SSD = Sequence[Sequence[dict]]
TSSD = tuple[SSD, SSD]


class Solver(AppLogger):
    def __init__(self, parent_logger: str, tf: TaskMetaFeatures):
        super().__init__(parent_logger=parent_logger)
        self.success = False
        self.tf = tf

    @abstractmethod
    def solve(self, x: SSD, y: SSD) -> bool:
        pass

    @abstractmethod
    def predict(self, x: SSD) -> SSD:
        pass


class Transformer(AppLogger):
    @abstractmethod
    def fit_transform(self, x: SSA, y: SSA) -> TSSD:
        pass

    @abstractmethod
    def transform_xtest(self, xtest: SSA) -> SSD:
        pass

    @abstractmethod
    def inverse_transform_xtest(self, xtest: SSD) -> SSD:
        pass


class Dictionarizer(Transformer):
    def __init__(
        self,
        parent_logger: str,
        *,
        exclude: set[str] | None = None,
        include: set[str] | None = None
    ):
        super().__init__(parent_logger)
        self.exclude = exclude
        self.include = include

    def fit_transform(self, x: SSA[Bag], y: SSA[Bag]) -> TSSD:
        x_ = TaskBags.to_dicts(x, exclude=self.exclude, include=self.include)
        y_ = TaskBags.to_dicts(y, exclude=self.exclude, include=self.include)
        return x_, y_

    def transform_xtest(self, xtest: SSA[Bag]) -> SSD:
        x_ = TaskBags.to_dicts(xtest, exclude=self.exclude, include=self.include)
        return x_

    def inverse_transform_xtest(self, xtest: SSD) -> SSD:
        return xtest


# constants are not deleted since there is no them in BK now
class ConstantsRemover(Transformer):
    def __init__(self, parent_logger: str):
        super().__init__(parent_logger)
        self.xconsts = {}
        self.yconsts = {}

    def _transform(self, data: SSD, exclude: set[str]) -> SSD:
        newxs = []
        keep_keys = data[0][0].keys() - exclude
        for e in data:
            new_e = []
            for d in e:
                new_e.append({k: d[k] for k in keep_keys})
            newxs.append(new_e)
        return newxs

    def fit_transform(self, x: SSD, y: SSD):
        xlgg = lgg.lgg_dict(list(lgg.lgg_dict(e) for e in x))
        self.xconsts = {k: v for k, v in xlgg.items() if v != lgg.VAR}
        newxs = self._transform(x, set(self.xconsts.keys()))

        ylgg = lgg.lgg_dict(list(lgg.lgg_dict(e) for e in y))
        self.yconsts = {k: v for k, v in ylgg.items() if v != lgg.VAR}
        newys = self._transform(y, set(self.yconsts.keys()))
        return newxs, newys

    def transform_xtest(self, xtest: SSD) -> SSD:
        return self._transform(xtest, set(self.xconsts.keys()))

    def inverse_transform_xtest(self, xtest: SSD) -> SSD:
        xcopy = copy(xtest)
        for e in xcopy:
            for d in e:
                d.update(self.yconsts)
        return xcopy


# TODO. Split into 3 separate solvers
class PrimitiveSolver(Solver):
    """Provides the simpliest relations between x's and y's.
    Namely: constant and one-to-one  relations and their combinations."""

    def __init__(self, parent_logger: str, tf: TaskMetaFeatures):
        super().__init__(parent_logger, tf)
        self.y_count: int | None = None
        self.y_vars: list[str] | None = None
        self.case1 = False
        self.case2 = False
        self.case3 = False

    def solve(self, x: SSD, y: SSD) -> bool:
        if self.tf.all_y_consts and self.tf.all_xy_same_len:
            self.case1 = True
            self.success = True
            self.logger.debug("y is constant and its number is 1to1 to x")
            return True
        if self.tf.all_y_consts and self.tf.all_y_const_len:
            self.case2 = True
            self.y_count = len(y[0])
            self.success = True
            self.logger.debug("y is constant and its number is constant too")
            return True
        if self.tf.all_xy_same_len:
            case3 = True
            y_vars = [k for k, v in self.tf.ylgg.items() if v == lgg.VAR]
            for xi, yi in zip(x, y):
                for _x, _y in zip(xi, yi):
                    for v in y_vars:
                        if _x[v] != _y[v]:
                            case3 = False
                            break
            if case3:
                self.y_vars = y_vars
                self.case3 = True
                self.success = True
                self.logger.debug("one2one relation between xs' and ys' fields")
        return False

    def predict(self, x: SSD) -> SSD:
        if not self.success:
            raise AttributeError("The solver has no solution.")
        if self.case1:
            res = []
            for xi in x:
                res.append([copy(self.tf.ylgg) for _ in range(len(xi))])
            return res
        if self.case2:
            res = []
            for _ in x:
                res_i = []
                res_i.append([copy(self.tf.ylgg) for _ in range(self.y_count)])
                res.append(res_i)
            return res
        if self.case3:
            res = []
            for xi in x:
                res_i = []
                for reg in xi:
                    _y = copy(self.tf.ylgg)
                    for k in self.y_vars:
                        _y[k] = reg[k]
                    res_i.append(_y)
                res.append(res_i)
            return res
        raise RuntimeError("Inconsistent state of the class.")
