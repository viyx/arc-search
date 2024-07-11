import numpy as np
from skimage.measure import label

from reprs.primitives import Bag, Region

# def _flatten_and_hash(data: np.ndarray, bg: int) -> str:
#     one_colored = len(np.unique(data)) == 1
#     if one_colored:
#         return str(data[0, 0])
#     bm = _add_bg(data, bg)
#     return str(hash(str(bm.flatten())))


# def _flatten_and_hash(data: np.ndarray) -> str:
#     one_colored = len(np.unique(data)) == 1
#     if one_colored:
#         return str(data[0, 0])
#     return str(hash(str(data.flatten())))


# def _add_bg(data: np.ndarray, bg: int) -> np.ndarray:
#     copy = np.array(data)
#     copy[data == bg] = -1
#     return copy


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
        bg_compress = True
        #  extract compressed regions
        #  will be only full rect bitmaps
        mask = np.full_like(data, -1)
        mask[(data != bg) & (data != -1)] = 1
        comps, ncomps = _label(mask, c, -1)
    else:
        comps, ncomps = _label(data, c, bg)
    regions = []
    for i in range(1, ncomps + 1):
        _mask = comps == i

        # find exterior rectangle
        xs, ys = np.where(_mask)
        xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)

        _d = data[xmin : xmax + 1, ymin : ymax + 1]
        if bg_compress:
            _b = np.ones_like(_d)
        else:
            _b = _mask[xmin : xmax + 1, ymin : ymax + 1]
        r = make_region(_d, _b, xmin, ymin, outdict)
        regions.append(r)
    return Bag(regions=regions, length=len(regions))
