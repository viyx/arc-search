import typing
from collections import defaultdict

import numpy as np
from sklearn.linear_model import LinearRegression

from datasets.arc import RawTaskData
from decompose.primitives import Region
from decompose.segment import extract_region_simple


def try_linear_mapping(x: list[int], y: list[int]) -> object | None:
    if len(x) != len(y):
        return None

    if any(not isinstance(v, int) for v in x) or any(not isinstance(v, int) for v in y):
        return None

    regr = LinearRegression().fit(np.array(x).reshape(-1, 1), y)
    if np.allclose(regr.coef_ // 1, regr.coef_):
        return regr
    return None


def _substitution(data: list[dict]) -> dict:
    sub = {k: v for k, v in data[0].items() if isinstance(v, typing.Hashable)}

    for d in data:
        for k in sub:
            if sub[k] == d[k]:
                continue
            sub[k] = "VAR"
    return sub


def lgg(data: list[list[Region]]) -> list[dict]:
    subs = []
    for regs in data:
        dicts = [r.model_dump() for r in regs]
        sub = _substitution(dicts)
        if sub == {}:
            return None
        subs.append(sub)
    return subs


def _adjust(data: list[Region], to: dict, hashes: dict) -> list[Region]:
    result = []
    for i, r in enumerate(data):
        _r = [r]
        for k, v in to.items():
            if v != "VAR":
                if getattr(r, k) != v and k == "shape":
                    _r = r.convert_shape(to, hashes)
                    break
        result.extend(_r)
    return result


def count_vars(subs: list[dict]) -> list[int]:
    return [sum(v == "VAR" for v in s.values()) for s in subs]


class TaskSearch:
    def __init__(self, task: RawTaskData) -> None:
        self.task = task
        self.success = False
        self.steps = defaultdict(dict)
        self.hashes = {}

    def solved(self, ylevel) -> dict:
        attrs = {}
        if ylevel in self.steps:
            for _, xlevel in self.steps[ylevel].items():
                for k, v in xlevel.items():
                    attrs[k] = v
        return attrs

    def search_topdown(self) -> None:
        xs = [extract_region_simple(x, self.hashes) for x in self.task.train_x]
        ys = [extract_region_simple(x, self.hashes) for x in self.task.train_y]

        max_ylevel = max(y.max_level() for y in ys)
        max_xlevel = max(x.max_level() for x in xs)
        for ylevel in range(max_ylevel):
            ylevel_data = [_y.get_level_data(ylevel) for _y in ys]
            level_succeed = False
            for xlevel in range(max_xlevel):
                xlevel_data = [_x.get_level_data(xlevel) for _x in xs]
                if self.step(ylevel_data, xlevel_data, ylevel, xlevel):
                    level_succeed = True
                    break
            if not level_succeed:
                print()
                # return
        self.success = True

    def step(self, ydata, xdata, ylevel, xlevel):
        step = {}
        ydata = self.try_adjust(ydata)
        xdata = self.try_adjust(xdata)
        ylgg = lgg(ydata)
        solved_attr = self.solved(ylevel)

        for attr in ylgg[0].keys() - solved_attr.keys():
            yattrs = [getattr(r, attr) for y in ydata for r in y]

            # write const
            if all(yattrs[0] == a for a in yattrs):
                step[attr] = yattrs[0]
                continue

            # write linmap
            xattrs = [getattr(r, attr) for x in xdata for r in x]
            if m := try_linear_mapping(xattrs, yattrs):
                step[attr] = m

        self.steps[ylevel][xlevel] = step
        if ylgg[0].keys() - solved_attr.keys() - step.keys() == set():
            return True
        return False

    def try_adjust(self, data):
        lggs = lgg(data)

        var_cnts = count_vars(lggs)
        if any((m := min(var_cnts)) < c for c in var_cnts):
            mi = var_cnts.index(m)
            etalon = lggs[mi]
            for i, c in enumerate(var_cnts):
                if c > m:
                    data[i] = _adjust(data[i], etalon, self.hashes)
        return data

    def test(self) -> list[np.ndarray] | None:
        results = []
        for x in self.task.test_x:
            xregs = extract_region_simple(x, self.hashes)

            data1 = self.create_level(xregs.get_level_data(1), self.steps[1])
            regs1 = [Region(**d, childs=[]) for d in data1]
            data0 = self.create_level(xregs.get_level_data(0), self.steps[0])
            res = Region(**data0[0], childs=regs1)
            results.append(res.render(self.hashes))
        return results

    def create_level(self, level_data, skeleton):
        attrs = {}
        for _, d in skeleton.items():
            attrs.update(d)

        result = []
        for x in level_data:
            _data = {}
            for k, v in attrs.items():
                if not isinstance(v, LinearRegression):
                    _data[k] = v
                elif isinstance(v, LinearRegression):
                    _x = np.array(getattr(x, k)).reshape(1, -1)
                    _data[k] = round(v.predict(_x)[0])
            result.append(_data)
        return result
