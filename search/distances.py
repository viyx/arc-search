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
        if exclude is not None and k in exclude:
            continue
        n += 1
        if k not in b:
            continue
        if isinstance(a[k], dict) and isinstance(b[k], dict):
            m += 1 - dict_keys_dist(a[k], b[k])
        else:
            m += 1
    return 1 - (m / n)
