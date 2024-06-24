from itertools import product
from queue import PriorityQueue

import numpy as np
from networkx import DiGraph

from datasets.arc import RawTaskData
from reprs.primitives import Bag
from search.distances import dict_keys_dist, pairwise_dists
from search.graph import add_topdown, make_regions
from search.inductions import fast11_induction
from search.lgg import lgg_prim

# def try_linear_mapping(x: list[int], y: list[int]) -> object | None:
#     if len(x) != len(y):
#         return None

#     if any(not isinstance(v, int) for v in x) or
# any(not isinstance(v, int) for v in y):
#         return None

#     regr = LinearRegression().fit(np.array(x).reshape(-1, 1), y)
#     if np.allclose(regr.coef_ // 1, regr.coef_):
#         return regr
#     return None


# def _substitution(data: list[dict]) -> dict:
#     sub = {k: v for k, v in data[0].items() if isinstance(v, typing.Hashable)}

#     for d in data:
#         for k in sub:
#             if sub[k] == d[k]:
#                 continue
#             sub[k] = "VAR"
#     return sub


# def lgg(data: list[list[Region]]) -> list[dict]:
#     subs = []
#     for regs in data:
#         dicts = [r.model_dump() for r in regs]
#         sub = _substitution(dicts)
#         if sub == {}:
#             return None
#         subs.append(sub)
#     return subs


# def _convert2shape(data: list[Region], to: dict, hashes: dict) -> list[Region]:
#     result = []
#     for r in data:
#         _r = [r]
#         for k, v in to.items():
#             if v != "VAR" and k == "shape" and getattr(r, k) != v:
#                 splitted = []
#                 if try_split2shape(r, to["shape"], hashes, splitted):
#                     _r = splitted
#                     break
#         result.extend(_r)
#     return result


# def count_vars(subs: list[dict]) -> list[int]:
#     return [sum(v == "VAR" for v in s.values()) for s in subs]


class TaskSearch:
    def __init__(self, task: RawTaskData) -> None:
        self.task = task
        self.success = False
        self.q = PriorityQueue()
        self.closed = []
        self.gx, self.gy = None, None

    def _put(self, xnode: str, ynode: str, dist: float) -> None:
        pair = f"{xnode}:{ynode}"
        t = (dist, pair)
        if pair not in self.closed:
            self.q.put(t)

    def _get(self) -> tuple[float, str, str]:
        dist, pair = self.q.get()
        return dist, *pair.split(":")

    def _init_search(self) -> None:
        self.gx, self.gy = DiGraph(), DiGraph()
        x_bags, x_hashes = make_regions(self.task.train_x, bg=-1)
        x_test_bags, x_test_hashes = make_regions(self.task.test_x, bg=-1)
        y_bags, y_hashes = make_regions(self.task.train_y, bg=-1)
        self.gx.add_node(
            "0",
            data=x_bags,
            hashes=x_hashes,
            test_data=x_test_bags,
            test_hashes=x_test_hashes,
        )
        self.gy.add_node("0", data=y_bags, hashes=y_hashes, solved_yet={})
        self._put("0", "0", 0)

    def search_topdown(self) -> None:
        self._init_search()
        while not self.q.empty() or self.success:
            _, xnode, ynode = self._get()

            xbags: list[Bag] = self.gx.nodes[xnode]["data"]
            ybags: list[Bag] = self.gy.nodes[ynode]["data"]

            solved_yet = self.gy.nodes[ynode]["solved_yet"]
            ind1 = fast11_induction(xbags, ybags, solved_yet)

            solved = np.isclose(dict_keys_dist(Bag.blank(), ind1, ["raw"]), 0)
            self.gy.nodes[ynode]["solved"] = solved
            self.gy.nodes[ynode]["solved_yet"] = {"xnode": xnode, "maps": ind1}

            if solved:
                raise NotImplementedError()
            new_ynodes = []
            for p in [-1, 0]:
                x_data = [r.raw for b in xbags for r in b.regions]
                y_data = [r.raw for b in ybags for r in b.regions]
                x_data_test = [
                    r.raw for b in self.gx.nodes[xnode]["test_data"] for r in b.regions
                ]

                add_topdown(self.gx, x_data, "repr", xnode, p, x_data_test)
                ynew = add_topdown(self.gy, y_data, "repr", ynode, p, solved_yet={})
                new_ynodes.append(ynew)

            self.closed.append(f"{xnode}:{ynode}")
            self.put(new_ynodes)

    def put(self, ynodes: list[str]) -> None:
        all_xnodes = self.gx.nodes
        x_lggs = [lgg_prim(self.gx.nodes[n]["data"]) for n in all_xnodes]
        y_lggs = [lgg_prim(self.gy.nodes[n]["data"]) for n in ynodes]

        # select nodes
        dists = np.ravel(pairwise_dists(x_lggs, y_lggs))
        pairs = list(product(all_xnodes, ynodes))
        for d, (xnode, ynode) in zip(dists, pairs):
            self._put(xnode, ynode, d)

    # def step(self, ydata, xdata, ylevel, xlevel):
    #     step = {}
    #     ydata = self.try_adjust(ydata)
    #     xdata = self.try_adjust(xdata)
    #     ylgg = lgg(ydata)
    #     solved_attr = self.solved(ylevel)

    #     for attr in ylgg[0].keys() - solved_attr.keys():
    #         yattrs = [getattr(r, attr) for y in ydata for r in y]

    #         # write const
    #         if all(yattrs[0] == a for a in yattrs):
    #             step[attr] = yattrs[0]
    #             continue

    #         # write linmap
    #         xattrs = [getattr(r, attr) for x in xdata for r in x]
    #         if m := try_linear_mapping(xattrs, yattrs):
    #             step[attr] = m

    #     self.steps[ylevel][xlevel] = step
    #     if ylgg[0].keys() - solved_attr.keys() - step.keys() == set():
    #         return True
    #     return False

    # def try_adjust(self, data):
    #     lggs = lgg(data)

    #     var_cnts = count_vars(lggs)
    #     if any((m := min(var_cnts)) < c for c in var_cnts):
    #         mi = var_cnts.index(m)
    #         etalon = lggs[mi]
    #         for i, c in enumerate(var_cnts):
    #             if c > m:
    #                 if etalon["shape"] != "VAR" and lggs[i]["shape"] == "VAR":
    #                     data[i] = _convert2shape(data[i], etalon, self.hashes)
    #     return data

    # def test(self) -> list[np.ndarray] | None:
    #     results = []

    #     def _test(self, x: Region, lvl: int):
    #         if lvl > x.max_level() or lvl > max(self.steps):
    #             raise ValueError("Level exceed maximum.")

    #         lvl_data = self.create_level(x.get_level_data(lvl), self.steps[lvl])
    #         if lvl == 0:
    #             return [
    #                 Region(**d, childs=[], childs_hash=childs_hash([], self.hashes))
    #                 for d in lvl_data
    #             ]
    #         childs = _test(self, x, lvl + 1)
    #         # ch = childs_hash(childs, self.hashes)
    #         return [Region(**d, childs=childs) for d in lvl_data]

    #     for x in self.task.test_x:
    #         xreg = extract_hierarchy(x, self.hashes)

    #         # data1 = self.create_level(xregs.get_level_data(1), self.steps[1])
    #         # regs1 = [Region(**d, childs=[]) for d in data1]
    #         # data0 = self.create_level(xregs.get_level_data(0), self.steps[0])
    #         # res = Region(**data0[0], childs=regs1)
    #         res = _test(self, xreg, 0)
    #         results.append(res.render(self.hashes))
    #     return results

    # def create_level(self, level_data, skeleton):
    #     attrs = {}
    #     for _, d in skeleton.items():
    #         attrs.update(d)

    #     result = []
    #     for x in level_data:
    #         _data = {}
    #         for k, v in attrs.items():
    #             if not isinstance(v, LinearRegression):
    #                 _data[k] = v
    #             elif isinstance(v, LinearRegression):
    #                 _x = np.array(getattr(x, k)).reshape(1, -1)
    #                 _data[k] = round(v.predict(_x)[0])
    #         result.append(_data)
    #     return result


# class TaskSearch:
#     def __init__(self, task: RawTaskData) -> None:
#         self.task = task
#         self.success = False
#         self.steps = defaultdict(dict)
#         self.hashes = {}

#     def solved(self, ylevel) -> dict:
#         attrs = {}
#         if ylevel in self.steps:
#             for _, xlevel in self.steps[ylevel].items():
#                 for k, v in xlevel.items():
#                     attrs[k] = v
#         return attrs

#     def search_topdown(self) -> None:
#         xs = [extract_hierarchy(x, self.hashes) for x in self.task.train_x]
#         ys = [extract_hierarchy(x, self.hashes) for x in self.task.train_y]

#         max_ylevel = max(y.max_level() for y in ys)
#         max_xlevel = max(x.max_level() for x in xs)
#         for ylevel in range(max_ylevel):
#             ylevel_data = [_y.get_level_data(ylevel) for _y in ys]
#             for xlevel in range(max_xlevel):
#                 xlevel_data = [_x.get_level_data(xlevel) for _x in xs]
#                 if self.step(ylevel_data, xlevel_data, ylevel, xlevel):
#                     self.success = True
#                     return

#     def step(self, ydata, xdata, ylevel, xlevel):
#         step = {}
#         ydata = self.try_adjust(ydata)
#         xdata = self.try_adjust(xdata)
#         ylgg = lgg(ydata)
#         solved_attr = self.solved(ylevel)

#         for attr in ylgg[0].keys() - solved_attr.keys():
#             yattrs = [getattr(r, attr) for y in ydata for r in y]

#             # write const
#             if all(yattrs[0] == a for a in yattrs):
#                 step[attr] = yattrs[0]
#                 continue

#             # write linmap
#             xattrs = [getattr(r, attr) for x in xdata for r in x]
#             if m := try_linear_mapping(xattrs, yattrs):
#                 step[attr] = m

#         self.steps[ylevel][xlevel] = step
#         if ylgg[0].keys() - solved_attr.keys() - step.keys() == set():
#             return True
#         return False

#     def try_adjust(self, data):
#         lggs = lgg(data)

#         var_cnts = count_vars(lggs)
#         if any((m := min(var_cnts)) < c for c in var_cnts):
#             mi = var_cnts.index(m)
#             etalon = lggs[mi]
#             for i, c in enumerate(var_cnts):
#                 if c > m:
#                     if etalon["shape"] != "VAR" and lggs[i]["shape"] == "VAR":
#                         data[i] = _convert2shape(data[i], etalon, self.hashes)
#         return data

#     def test(self) -> list[np.ndarray] | None:
#         results = []

#         def _test(self, x: Region, lvl: int):
#             if lvl > x.max_level() or lvl > max(self.steps):
#                 raise ValueError("Level exceed maximum.")

#             lvl_data = self.create_level(x.get_level_data(lvl), self.steps[lvl])
#             if lvl == 0:
#                 return [
#                     Region(**d, childs=[], childs_hash=childs_hash([], self.hashes))
#                     for d in lvl_data
#                 ]
#             childs = _test(self, x, lvl + 1)
#             # ch = childs_hash(childs, self.hashes)
#             return [Region(**d, childs=childs) for d in lvl_data]

#         for x in self.task.test_x:
#             xreg = extract_hierarchy(x, self.hashes)

#             # data1 = self.create_level(xregs.get_level_data(1), self.steps[1])
#             # regs1 = [Region(**d, childs=[]) for d in data1]
#             # data0 = self.create_level(xregs.get_level_data(0), self.steps[0])
#             # res = Region(**data0[0], childs=regs1)
#             res = _test(self, xreg, 0)
#             results.append(res.render(self.hashes))
#         return results

#     def create_level(self, level_data, skeleton):
#         attrs = {}
#         for _, d in skeleton.items():
#             attrs.update(d)

#         result = []
#         for x in level_data:
#             _data = {}
#             for k, v in attrs.items():
#                 if not isinstance(v, LinearRegression):
#                     _data[k] = v
#                 elif isinstance(v, LinearRegression):
#                     _x = np.array(getattr(x, k)).reshape(1, -1)
#                     _data[k] = round(v.predict(_x)[0])
#             result.append(_data)
#         return result
