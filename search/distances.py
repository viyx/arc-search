from reprs.primitives import Bag


def lgg_dist(lgg1: dict, lgg2: dict) -> float:
    """Like an edit distance. The more different values btw lgg's
    the greater the distance. Evaluate complex fields recursively."""
    n = 0
    m = 0
    for k in lgg1:
        n += 1
        if k not in lgg2:
            continue
        if isinstance(lgg1[k], dict) and isinstance(lgg2[k], dict):
            m += 1 - lgg_dist(lgg1[k], lgg2[k])
        elif lgg1[k] != "VAR" and lgg1[k] == lgg2[k]:
            m += 1
    return 1 - m / n


def pairwise_dists(l1: list[dict], l2: list[dict]) -> list:
    return [[lgg_dist(d1, d2) for d2 in l2] for d1 in l1]


# def dict_keys_dist(a: dict, b: dict, exclude: list[str] | None = None):
#     n = 0
#     m = 0
#     for k in a:
#         if exclude and k in exclude:
#             continue
#         n += 1
#         if k not in b:
#             continue
#         if isinstance(a[k], dict) and isinstance(b[k], dict):
#             m += 1 - dict_keys_dist(a[k], b[k])
#         else:
#             m += 1
#     return 1 - (m / n)


def edit_like(xbags: list[Bag], ybags: list[Bag]) -> int:
    "Like an edit-distance. Counts how many symbols different from x's are in y's."
    edit_dist = 0
    y_symbols = set()
    for x, y in zip(xbags, ybags):
        xsymbols = x.soup_of_props
        for r in y.regions:
            if r.visual_hash in xsymbols:
                continue
            if r.mask_hash in xsymbols:
                edit_dist += len(r.unq_colors)  # recolor

        ysymbols = y.soup_of_props
        y_new_symbols = ysymbols - xsymbols - y_symbols
        edit_dist += len(y_new_symbols)
        y_symbols |= y_new_symbols
    return edit_dist


def ribl_max(xbags: list[Bag], ybags: list[Bag]) -> int:
    "Rough RIBL distance."
    dists = []
    for x, y in zip(xbags, ybags):
        xsymbols = x.soup_of_props
        ysymbols = y.soup_of_props
        dist = len(ysymbols - xsymbols)
        dist += abs(len(x.regions) - len(y.regions))
        dists.append(dist)
    return max(dists)
