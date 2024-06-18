from reprs.primitives import Bag


def _lgg_dist(lgg1: dict, lgg2: dict) -> float:
    n = 0
    m = 0
    for k in lgg1:
        if k in lgg2:
            n += 1
            if lgg1[k] == lgg2[k]:
                m += 1
        else:
            return 1
    return m / n


def bag_dist(b1: Bag, b2: Bag):
    pass


def pairwise_dists(l1: list[dict], l2: list[dict]) -> list:
    return [[_lgg_dist(d1, d2) for d2 in l2] for d1 in l1]
