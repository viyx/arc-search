from collections import defaultdict
from typing import Iterable

VAR = "VAR"


def lgg_dict(data: list[dict]) -> dict:
    first = data[0].copy()
    for d in data:
        for k in first:
            if first[k] == d[k] and d[k] != VAR:
                continue
            first[k] = VAR
    return first


def lgg_ext(data: Iterable[dict]) -> dict:
    res = defaultdict(list)
    for d in data:
        for k, v in d.items():
            res[k].append(v)
    for k, v in res.items():
        if len(set(v)) == 1:
            res[k] = v[0]
    return dict(res)


# def merge_lgg_ext(data: Iterable[dict]) -> dict:
#     res = defaultdict(list)
#     for d in data:
#         for k, v in d.items():
#             if isinstance(k, list):
#                 res[k].extend(v)
#             else:
#                 res[k].append(v)
#     for k, v in res.items():
#         if len(set(v)) == 1:
#             res[k] = v[0]
#     return dict(res)
