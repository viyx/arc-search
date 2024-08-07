import numpy as np
from skimage.measure import label

from reprs.primitives import Bag, Region

# def extract_bags_from_raw(f, data: list[np.ndarray], c: int, bg: int) -> list[Bag]:
#     bags = []
#     for x in data:
#         h = {}
#         b = f(x, h, c, bg)
#         if len(b.regions) > 0:
#             bags.append(b)
#         else:
#             raise NotImplementedError("Check consistnecy.")
#     return bags


def _label(data: np.ndarray, c: int, bg: int) -> tuple[np.ndarray, int]:
    if c == -1:  # no connectivity, return 1-pixel components
        mask = data != bg
        ncomps = mask.sum()
        comps = np.full_like(data, -1, dtype=int)
        comps[mask] = np.arange(1, ncomps + 1)
        return comps, ncomps
    if c in [1, 2]:
        return label(data, return_num=True, background=bg, connectivity=c)


def extract_regions(data: np.ndarray, c: int, bg: int) -> Bag:
    # remove background, cut full regions
    # if bg not in data or bg == -1 or c == -1:
    # raise ValueError("Consistency error. Impossible action.")
    mask = np.full_like(data, -1)
    mask[(data != bg) & (data != -1)] = 1
    comps, ncomps = _label(mask, c, -1)
    regions = []
    for i in range(1, ncomps + 1):
        _mask = comps == i

        # find bounding rectangle
        xs, ys = np.where(_mask)
        xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)

        _d = data[xmin : xmax + 1, ymin : ymax + 1]
        _b = np.ones_like(_d)
        r = Region(x=xmin, y=ymin, raw=_d, mask=_b)
        regions.append(r)
    return Bag(regions=regions, length=len(regions))


def extract_prims(data: np.ndarray, c: int, bg: int) -> Bag:
    comps, ncomps = _label(data, c, bg)
    regions = []
    for i in range(1, ncomps + 1):
        _mask = comps == i

        # find bounding rectangle
        xs, ys = np.where(_mask)
        xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)

        _d = data[xmin : xmax + 1, ymin : ymax + 1]
        _b = np.full_like(_d, -1)
        _b[_mask[xmin : xmax + 1, ymin : ymax + 1]] = 1
        r = Region(x=xmin, y=ymin, raw=_d, mask=_b)
        regions.append(r)
    return Bag(regions=regions, length=len(regions))
