def lgg_dist(lgg1: dict, lgg2: dict) -> float:
    n = 0
    m = 0
    for k in lgg1:
        n += 1
        if k not in lgg2:
            continue
        if isinstance(lgg1[k], dict) and isinstance(lgg2[k], dict):
            m += lgg_dist(lgg1[k], lgg2[k])
        elif lgg1[k] != "VAR" and lgg1[k] == lgg2[k]:
            m += 1
    return m / n


def pairwise_dists(l1: list[dict], l2: list[dict]) -> list:
    return [[lgg_dist(d1, d2) for d2 in l2] for d1 in l1]


def dict_dist(d_from: dict, d_to: dict):
    n = 0
    m = 0
    for k in d_from:
        n += 1
        if k not in d_to:
            continue
        if isinstance(d_from[k], dict) and isinstance(d_to[k], dict):
            m += dict_dist(d_from[k], d_to[k])
        else:
            m += 1
    return m / n
