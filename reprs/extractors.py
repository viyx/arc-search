import numpy as np
from skimage.measure import label

from reprs.primitives import NO_BG, Bag, Region

NO_CONN = -1
FOUR_CONN = 1
EIGHT_CONN = 2
CONNECTIVITY = [NO_CONN, FOUR_CONN, EIGHT_CONN]


def _label(data: np.ndarray, c: int, bg: int) -> tuple[np.ndarray, int]:
    """Extended version of `skimage.measure.label` with no-connectivity option.
    In `NO_CONN` case all `pixel` blocks extracted as separate regions."""
    if c == NO_CONN:
        if data.dtype != bool:
            mask = data != bg
        else:
            mask = data
        ncomps = mask.sum()
        comps = np.full_like(data, NO_BG, dtype=int)
        comps[mask] = np.arange(1, ncomps + 1)
        return comps, ncomps
    if c in [1, 2]:
        return label(data, return_num=True, background=bg, connectivity=c)
    raise ValueError("Not supported connectivity.")


def extract_regions(data: np.ndarray, bg: int, c: int) -> Bag:
    "Assume all non-bg colors are the same and extract components."
    mask = (data != bg) & (data != NO_BG)
    comps, ncomps = _label(mask, c, NO_BG)
    regions = []
    for i in range(1, ncomps + 1):
        _mask = comps == i
        xs, ys = np.where(_mask)
        xfrom, xto, yfrom, yto = min(xs), max(xs), min(ys), max(ys)

        d = data[xfrom : xto + 1, yfrom : yto + 1]
        m = np.full_like(d, True, dtype=bool)
        r = Region(x=xfrom, y=yfrom, raw=d, mask=m)
        regions.append(r)
    return Bag(regions=tuple(regions))


def extract_prims(data: np.ndarray, c: int, bg: int) -> Bag:
    "Extract primitives as standard `label` do."
    comps, ncomps = _label(data, c, bg)
    regions = []
    for i in range(1, ncomps + 1):
        mask = comps == i
        xs, ys = np.where(mask)
        xfrom, xto, yfrom, yto = min(xs), max(xs), min(ys), max(ys)

        d = data[xfrom : xto + 1, yfrom : yto + 1]
        m = mask[xfrom : xto + 1, yfrom : yto + 1]
        r = Region(x=xfrom, y=yfrom, raw=d, mask=m)
        regions.append(r)
    return Bag(regions=tuple(regions))
