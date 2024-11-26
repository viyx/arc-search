from functools import cached_property

from reprs.primitives import Region, TaskBags
from search import lgg


class TaskMetaFeatures:
    "Contains high-level features of a task."

    def __init__(self, task: TaskBags, **kwargs) -> None:
        self.str_fields = Region.content_props()
        self._task = task
        self.ylggs = [lgg.lgg_ext(b.dump_main_props(**kwargs)) for b in task.y]
        self.ylgg = lgg.lgg_dict(self.ylggs)

    @cached_property
    def all_y_consts(self) -> bool:
        return all(v != lgg.VAR for v in self.ylgg.values())

    @cached_property
    def all_y_const_len(self) -> bool:
        first = len(self._task.y[0].regions)
        return all(first == len(b.regions) for b in self._task.y)

    @cached_property
    def all_xy_same_len(self) -> bool:
        return all(
            len(_y.regions) == len(_x.regions)
            for _x, _y in zip(self._task.x, self._task.y)
        )

    @cached_property
    def all_x_is_primitive(self) -> bool:
        return all(all(r.is_primitive for r in b) for b in self._task.x)

    @cached_property
    def all_y_is_primitive(self) -> bool:
        return all(all(r.is_primitive for r in b) for b in self._task.y)

    @cached_property
    def all_y_pixels(self) -> bool:
        return all(b.all_pixels for b in self._task.y)

    @cached_property
    def all_x_pixels(self) -> bool:
        return all(b.all_pixels for b in self._task.x)

    @cached_property
    def all_xtest_is_primitive(self) -> bool:
        return all(all(r.is_primitive for r in b) for b in self._task.x_test)

    @cached_property
    def all_y_colors_in_x(self) -> bool:
        for x, y in zip(self._task.x, self._task.y):
            if y.unq_colors.isdisjoint(x.unq_colors) or y.unq_colors > x.unq_colors:
                return False
        return True

    @cached_property
    def all_test_str_in_x(self) -> bool:
        for s in self.str_fields:
            xs = {getattr(r, s) for b in self._task.x for r in b.regions}
            xs_test = {getattr(r, s) for b in self._task.x_test for r in b.regions}
            if xs_test.isdisjoint(xs) or xs_test > xs:
                return False
        return True

    def len_x(self) -> int:
        return len(self._task.x)
