from typing import Hashable

from reprs.primitives import Bag, Region
from search.lgg import lgg_prim


def fast11_induction(
    xbags: list[Bag | Region], ybags: list[Bag | Region], exclude: dict | None = None
) -> dict:
    result = {}
    if len(xbags) != len(ybags):
        return result
    search_bag_fields = ybags[0].model_hashable_fields
    if exclude:
        search_bag_fields = ybags[0].model_hashable_fields - exclude.keys()
    for f in search_bag_fields:
        if not isinstance(getattr(ybags[0], f), Hashable):
            x_flatten_regions = [r for x in xbags for r in x.regions]
            y_flatten_regions = [r for x in ybags for r in x.regions]
            ex_ = exclude.get(f) if exclude else None
            result[f] = fast11_induction(x_flatten_regions, y_flatten_regions, ex_)
            continue
        else:
            xa = [getattr(b, f) for b in xbags]
            ya = [getattr(b, f) for b in ybags]
            const_rel = find_consts_rels(xa, ya)

            # FROMX
            if const_rel:
                result[f] = "FROMX"
                continue

            # CONST
            if all(ya[0] == y_ for y_ in ya):
                result[f] = ya[0]
        # for f in search_bag_fields:
        #     rels_dummy = find_consts_rels(xregs_lgg, yregs_lgg)
        # rels_maps = find_maps_rels(xbags, ybags, xbags_test, rels_dummy)
        # sol = {"length": "FROM_X", "regions": {**rels_dummy, **rels_maps}}
        # return sol
    return result


# def find_consts_rels(x: dict, y: dict, exclude: dict) -> dict:
#     rels = {}
#     for yk in y.keys() - exclude:
#         if y[yk] == "VAR":
#             continue
#         for xk, xv in x.items():
#             if xv == y[yk]:
#                 rels[yk] = f"FROM_X_{xk}"
#                 break
#     return rels


def find_consts_rels(x: list[int], y: list[int]) -> bool:
    for a, b in zip(x, y):
        if a != b:
            return False
    return True


def _dict_rel(a: list[str], b: list[str]) -> bool | dict:
    rel = {}
    for x, y in zip(a, b):
        if x not in rel:
            rel[x] = y
        else:
            if rel[x] != y:
                return False
    return rel


def find_maps_rels(
    xbags: list[Bag], ybags: list[Bag], xbags_test: list[Bag], exclude: dict
) -> dict:
    search_fields = lgg_prim(xbags[0].regions).keys() - exclude.keys()

    maps = {}
    for f in search_fields:
        xkeys = [getattr(r, f) for b in xbags for r in b.regions]
        ykeys = [getattr(r, f) for b in ybags for r in b.regions]
        xkeys_test = [getattr(r, f) for b in xbags_test for r in b.regions]
        if all(x in xkeys for x in xkeys_test):
            o2o = _dict_rel(xkeys, ykeys)
            if o2o:
                maps[f] = o2o
    return maps
