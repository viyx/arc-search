from functools import cached_property

import search.lgg as lgg
from reprs.primitives import Region, TaskBags
from search.answer import Answer
from search.prolog.aleph import Aleph
from search.prolog.bg import BASE_BG

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


class TaskMetaFeatures:
    def __init__(self, task: TaskBags) -> None:
        self.str_fields = Region.shortcuts_props()
        self.all_fields = Region.main_props()
        self._task = task
        self.x_lggs = [lgg.lgg_ext(b.dump_main_props()) for b in task.x]
        self.y_lggs = [lgg.lgg_ext(b.dump_main_props()) for b in task.y]
        self.test_lggs = [lgg.lgg_ext(b.dump_main_props()) for b in task.x_test]

    @cached_property
    def all_x_is_primitive(self) -> bool:
        return all(all(r.is_primitive for r in b) for b in self._task.x)

    @cached_property
    def all_xtest_is_primitive(self) -> bool:
        return all(all(r.is_primitive for r in b) for b in self._task.x_test)

    @cached_property
    def all_y_colors_in_x(self) -> bool:
        for x, y in zip(self._task.x, self._task.y):
            if y.unq_colors.isdisjoint(x.unq_colors) or y.unq_colors > x.unq_colors:
                return False
        return True

    # def all_y_in_x(self, field: str) -> bool:
    #     for x, y in zip(self.x_lggs, self.y_lggs):
    #         if set(y[field]) <= set(x[field]):
    #             return False
    #     return True

    # def any_y_in_x(self, field: str) -> bool:
    #     for x, y in zip(self.x_lggs, self.y_lggs):
    #         if not set(y[field]).isdisjoint(set(x[field])):
    #             return True
    #     return False

    @cached_property
    def all_test_str_in_x(self) -> bool:
        for s in self.str_fields:
            xs = {getattr(r, s) for b in self._task.x for r in b.regions}
            xs_test = {getattr(r, s) for b in self._task.x_test for r in b.regions}
            if xs_test.isdisjoint(xs) or xs_test > xs:
                return False
        return True


# class Solver(ABC):
#     @abstractmethod
#     def try_solve(self, task: TaskBags, tf: TaskMetaFeatures, sofar: Answer) -> None:
#         pass


# class ConstantSolver:
#     def try_solve(self, y_lggs: list[dict]) -> None:
#         y_lgg = lgg.lgg_dict(y_lggs)

#         for k, v in y_lgg.items():
#             if v != lgg.VAR_CONST:
#                 sofar.add_const(k, v)
# ConstantSolver().try_solve(None, tf, sofar)


def exec_meta(task: TaskBags, sofar: Answer) -> None:
    tf = TaskMetaFeatures(task)

    if tf.all_test_str_in_x:
        a = Aleph(bg=BASE_BG)
        a.write_file(TaskBags.to_dicts(task.x), TaskBags.to_dicts(task.y))
    pass
    # a.induce()
    # if a.success:
    # res: list[str] = a.predict(task.x_test)
    # res =  Bag.from_strings(res)
    # return res
    # else:
    # pass
    # ConstantSolver().try_solve(None, tf, sofar)
    # One2OneMapSolver().try_solve(None, tf, sofar)
