from reprs.primitives import Bag


def lgg_dist(lgg1: dict, lgg2: dict) -> float:
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


def dict_keys_dist(a: dict, b: dict, exclude: list[str] | None = None):
    n = 0
    m = 0
    for k in a:
        if exclude and k in exclude:
            continue
        n += 1
        if k not in b:
            continue
        if isinstance(a[k], dict) and isinstance(b[k], dict):
            m += 1 - dict_keys_dist(a[k], b[k])
        else:
            m += 1
    return 1 - (m / n)


def dl(xbags: list[Bag], ybags: list[Bag]) -> int:
    desc_len = 0
    y_symbols = set()
    for _x, _y in zip(xbags, ybags):
        xsymbols = _x.soup_of_props
        for r in _y.regions:
            if r.visual_hash in xsymbols:
                continue
            if r.mask_hash in xsymbols:
                desc_len += len(r.unq_colors)  # recolor

        ysymbols = _y.soup_of_props
        y_new_symbols = ysymbols - xsymbols - y_symbols
        desc_len += len(y_new_symbols)
        y_symbols |= y_new_symbols
    return desc_len
