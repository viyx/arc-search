import numpy as np
from skimage.measure import label

from reprs.primitives import Bag, Region


def make_region(
    data: np.ndarray, bitmap: np.ndarray, x: int, y: int, outdict: dict
) -> Region:
    b_ = bitmap
    if bitmap.dtype == bool:
        b_ = np.full_like(bitmap, -1, dtype=int)
        b_[bitmap] = 1
    r = Region(x=x, y=y, height=data.shape[0], width=data.shape[1], raw=data, bitmap=b_)
    if len(r.raw_hash) > 1:
        outdict[r.raw_hash] = data
    return r


def _label(data: np.ndarray, c: int, bg: int) -> tuple[np.ndarray, int]:
    if c == -1:  # no connectivity, return 1-pixel components
        raise NotImplementedError()
        # mask = data != bg
        # ncomps = mask.sum()
        # comps = np.copy(data)
        # comps[mask] = np.arange(1, ncomps+1)
        # return comps, ncomps
    if c in [1, 2]:
        # _d = _add_bg(data, bg)
        return label(data, return_num=True, background=bg, connectivity=c)
    raise NotImplementedError()


def extract_bag(data: np.ndarray, outdict: dict, c: int, bg: int) -> Bag:
    bg_compress = False
    if bg in data and bg != -1:
        # remove background, cut full regions
        bg_compress = True
        mask = np.full_like(data, -1)
        mask[(data != bg) & (data != -1)] = 1
        comps, ncomps = _label(mask, c, -1)
    else:
        comps, ncomps = _label(data, c, -1)
    regions = []
    for i in range(1, ncomps + 1):
        _mask = comps == i

        # find bounding rectangle
        xs, ys = np.where(_mask)
        xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)

        _d = data[xmin : xmax + 1, ymin : ymax + 1]
        if bg_compress:
            # create new region
            _b = np.ones_like(_d)
            # _b[_d == -1] = -1  # clone bg
        else:
            # repeat bg from cut region
            _b = _mask[xmin : xmax + 1, ymin : ymax + 1]
            # _d[~_b] = -1
        r = make_region(_d, _b, xmin, ymin, outdict)
        regions.append(r)
    return Bag(regions=regions, length=len(regions))
