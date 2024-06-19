from reprs.primitives import Bag
from search.lgg import lgg_dict, lgg_prim


def induction(xbags: list[Bag], ybags: list[Bag], xbags_test: list[Bag]) -> dict:
    xs_bags_lgg = lgg_prim(xbags)
    ys_bags_lgg = lgg_prim(ybags)
    xs_test = lgg_prim(xbags_test)

    # will be more parameters
    # we are inside 1-1 bag
    if xs_bags_lgg["length"] == ys_bags_lgg["length"] == xs_test["length"]:
        # find funcss
        xregs_lgg = lgg_dict([lgg_prim(x.regions) for x in xbags])
        yregs_lgg = lgg_dict([lgg_prim(x.regions) for x in ybags])
        # xregs_test_lgg = _lgg([lgg(x.regions) for x in xbags_test])

        rels_dummy = find_consts_rels(xregs_lgg, yregs_lgg)
        rels_maps = find_maps_rels(xbags, ybags, xbags_test, rels_dummy)
        sol = {"length": "FROM_X", "regions": {**rels_dummy, **rels_maps}}
        return sol
    return {}


def find_consts_rels(x: dict, y: dict) -> dict:
    rels = {}
    for yk, yv in y.items():
        if yv == "VAR":
            continue
        for xk, xv in x.items():
            if xv == yv:
                rels[yk] = f"FROM_X_{xk}"
                break
    return rels


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
            if isinstance(o2o, dict):
                maps[f] = o2o
    return maps
