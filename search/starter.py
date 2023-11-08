from collections import Counter

import numpy as np

from datasets.arc import RawTaskData
from decompose.primitives import RectPrimitive, Region
from decompose.segment import extract_topdown


def find_mapping(x: list[int], y: list[int]) -> dict | None:
    if len(x) != len(y):
        raise NotImplementedError()

    m = {}
    for _x, _y in zip(x, y):
        if _x in m:
            if not m[_x] == _y:
                return None
            continue
        m[_x] = _y
    return m


def xy_lgg(x: list, y: list) -> dict:
    # TODO Add x_lgg for childs
    expr = {}
    zero = y[0]
    if not all(map(lambda pair: isinstance(pair[0], type(pair[1])), zip(x, y))):
        assert NotImplementedError("Different types in x and y.")
    for attr in zero.model_dump():
        same = all(
            map(
                lambda pair: getattr(pair[0], attr) == getattr(pair[1], attr), zip(x, y)
            )
        )
        var_or_const = "VAR"
        if not same:
            if all(map(lambda _y: getattr(zero, attr) == getattr(_y, attr), y)):
                var_or_const = getattr(zero, attr)
        expr[attr] = "FROMX" if same else var_or_const
    return expr


def x_lgg_bm(x: list[RectPrimitive]) -> dict:
    if not all(map(lambda _x: isinstance(_x, RectPrimitive), x)):
        raise NotImplementedError()

    expr = {}
    zero = dict(x[0])  # convert BaseModel to dict
    for attr in zero:
        same = all(map(lambda _x: getattr(_x, attr) == zero[attr], x))
        expr[attr] = zero[attr] if same else "VAR"
    return expr


def x_lgg(x: list[dict]) -> dict:
    expr = {}
    zero = x[0]
    for attr in zero:
        same = all(map(lambda _x: _x[attr] == zero[attr], x))
        expr[attr] = zero[attr] if same else "VAR"
    return expr


def x_lgg_bm_childs(x: list[list[RectPrimitive]]) -> list[dict]:
    exprs = []
    for _x in x:
        expr = x_lgg_bm(_x)
        exprs.append(expr)
    return exprs


def refine_types(x: list[Region | RectPrimitive]):
    xs = x
    tc = Counter(map(type, x))
    if len(tc.keys()) > 1:
        xs = []
        for _x in x:
            if isinstance(_x, RectPrimitive):
                xs.append(_x.convert2region())
                continue
            xs.append(_x)
    return xs


def refine_childs_shape(x: list[list[RectPrimitive]]):
    lens = list(map(len, x))
    xs = x
    if 1 in lens:  # can convert one big prim to small ones
        ones_indices = [i for i, l in enumerate(lens) if l == 1]
        multi_indices = [i for i, l in enumerate(lens) if l != 1]
        exprs = x_lgg_bm_childs(x)
        big_one = exprs[ones_indices[0]]
        if all(
            map(
                lambda i: exprs[i]["width"] == big_one["width"]
                and exprs[i]["height"] == big_one["height"],
                ones_indices,
            )
        ):
            least_one = exprs[multi_indices[0]]
            if all(
                map(
                    lambda i: exprs[i]["width"] == least_one["width"]
                    and exprs[i]["height"] == least_one["height"],
                    multi_indices,
                )
            ):
                for i in ones_indices:
                    if xs[i][0].can_split_to_shape(
                        least_one["width"], least_one["height"]
                    ):
                        xs[i] = xs[i][0].convert_to_shape(
                            least_one["width"], least_one["height"]
                        )
    return xs


class TaskSearch:
    def __init__(self, task: RawTaskData) -> None:
        self.task = task
        self.success = False
        self.steps = []

    def search_topdown(self) -> None:
        xs = [extract_topdown(x) for x in self.task.train_x]
        ys = [extract_topdown(x) for x in self.task.train_y]

        xs, ys = self._make_step(xs, ys)

        if all(map(lambda _y: "childs" in _y.model_dump(), ys)):
            xs = list(map(lambda _x: _x.childs, xs))
            ys = list(map(lambda _y: _y.childs, ys))
            self._make_step_childs(xs, ys)
        print(self.success)

    def _make_step(self, x, y) -> tuple:
        x = refine_types(x)
        y = refine_types(y)

        lgg = xy_lgg(x, y)
        for k, v in lgg.items():
            if v == "VAR" and k != "childs":
                raise NotImplementedError()
        lgg["class"] = y[0].name()
        self.steps.append(lgg)
        print()
        return x, y

    def _make_step_childs(self, x, y):
        x = refine_childs_shape(x)
        y = refine_childs_shape(y)

        xy_lggs = []
        for _x, _y in zip(x, y):
            xy_lggs.append(xy_lgg(_x, _y))

        lgg = x_lgg(xy_lggs)
        c = Counter(lgg.values())
        if c.get("VAR") == 1:
            y_key = [k for k, v in lgg.items() if v == "VAR"][0]
            ys = [getattr(c, y_key) for _y in y for c in _y]
            _x_lgg = x_lgg(x_lgg_bm_childs(x))
            x_keys = [k for k, v in _x_lgg.items() if v == "VAR"]
            for _k in x_keys:
                xs = [getattr(c, _k) for _x in x for c in _x]
                m = find_mapping(xs, ys)
                if m is not None:
                    self.success = True
                    lgg[y_key] = (_k, m)
                    lgg["class"] = y[0][0].name()
                    self.steps.append(lgg)
                    break

    def test(self) -> list[np.ndarray] | None:
        if not self.success:
            return None

        xs = [extract_topdown(x) for x in self.task.test_x]
        if len(xs) > 1:
            raise NotImplementedError()

        def mapper(src: dict, step: dict, attrs: list) -> dict:
            data = {}
            for attr in attrs:
                target = step[attr]
                if target == "FROMX":
                    data[attr] = getattr(src, attr)
                elif isinstance(target, tuple):
                    m1, m2 = target
                    data[attr] = m2[getattr(src, m1)]
                else:
                    data[attr] = target
            return data

        results = []
        for x in xs:
            step_one = self.steps[0]
            if self.steps[0]["class"] == "region":
                attrs = ["x", "y", "width", "height", "background"]
                reg_data = mapper(x, step_one, attrs)
                if step_one["childs"] == "VAR":
                    step_two = self.steps[1]
                    childs = []
                    for c in x.childs:
                        if step_two["class"] != "rectprimitive":
                            raise NotImplementedError()
                        attrs = ["x", "y", "width", "height", "color"]
                        childs.append(RectPrimitive(**mapper(c, step_two, attrs)))
                    reg_data["childs"] = childs
                res = Region(**reg_data)
            results.append(res.to_numpy())
        return results
