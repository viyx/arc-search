import numpy as np
from skimage.measure import label

from reprs.primitives import NO_BG, Bag, Region

NO_CONN = -1
FOUR_CONN = 1
EIGHT_CONN = 2
CONNECTIVITY = [NO_CONN, FOUR_CONN, EIGHT_CONN]


def _label(data: np.ndarray, c: int, bg: int) -> tuple[np.ndarray, int]:
    if c == NO_CONN:  # no connectivity, return 1-pixel components
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
    mask = (data != bg) & (data != NO_BG)
    comps, ncomps = _label(mask, c, NO_BG)
    regions = []
    for i in range(1, ncomps + 1):
        _mask = comps == i

        # find bounding rectangle
        xs, ys = np.where(_mask)
        xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)

        _d = data[xmin : xmax + 1, ymin : ymax + 1]
        _b = np.full_like(_d, True, dtype=bool)
        r = Region(x=xmin, y=ymin, raw=_d, mask=_b)
        regions.append(r)
    return Bag(regions=tuple(regions))


def extract_prims(data: np.ndarray, c: int, bg: int) -> Bag:
    comps, ncomps = _label(data, c, bg)
    regions = []
    for i in range(1, ncomps + 1):
        _mask = comps == i

        # find bounding rectangle
        xs, ys = np.where(_mask)
        xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)

        _d = data[xmin : xmax + 1, ymin : ymax + 1]
        _b = _mask[xmin : xmax + 1, ymin : ymax + 1]
        r = Region(x=xmin, y=ymin, raw=_d, mask=_b)
        regions.append(r)
    return Bag(regions=tuple(regions))
