from functools import cached_property

from reprs.primitives import Region, TaskBags
from search import lgg


class TaskMetaFeatures:
    def __init__(self, task: TaskBags, *, exclude: set[str] | None = None) -> None:
        self.exclude = exclude
        self.str_fields = Region.content_props()
        # self.all_fields = Region.main_props()
        self._task = task
        # self.x_lggs = [lgg.lgg_ext(b.dump_main_props()) for b in task.x]
        self.ylggs = [lgg.lgg_ext(b.dump_main_props(exclude=exclude)) for b in task.y]
        self.ylgg = lgg.lgg_dict(self.ylggs)
        # self.test_lggs = [lgg.lgg_ext(b.dump_main_props()) for b in task.x_test]

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
