from typing import Hashable

from reprs.primitives import Bag, Region


def lgg_dict(data: list[dict]) -> dict:
    first = data[0]
    _lgg_dict = {k: v for k, v in first.items() if isinstance(v, Hashable)}

    for d in data:
        for k in _lgg_dict:
            if _lgg_dict[k] == d[k]:
                continue
            _lgg_dict[k] = "VAR"
    return _lgg_dict


def lgg_prim(data: list[Bag | Region]) -> list[dict]:
    _l = lgg_dict([r.model_dump() for r in data])
    if isinstance(data[0], Bag):
        _l["regions"] = lgg_dict(list(lgg_prim(b.regions) for b in data))
    return _l
