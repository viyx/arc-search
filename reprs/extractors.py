import numpy as np
from skimage.measure import label

from reprs.primitives import Bag, Region


def _flatten_and_hash(data: np.ndarray, bg: int) -> str:
    one_colored = len(np.unique(data)) == 1
    if one_colored:
        return str(data[0, 0])
    bm = _add_bg(data, bg)
    return str(hash(str(bm.flatten())))


def _add_bg(data: np.ndarray, bg: int) -> np.ndarray:
    copy = np.array(data)
    copy[data == bg] = -1
    return copy


def make_region(data: np.ndarray, x: int, y: int, outdict: dict, bg: int) -> Region:
    r = Region(
        x=x,
        y=y,
        raw_hash=_flatten_and_hash(data, bg),
        height=data.shape[0],
        width=data.shape[1],
        raw=_add_bg(data, bg),
    )
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
    elif c in [1, 2]:
        _d = _add_bg(data, bg)
        return label(_d, return_num=True, background=bg, connectivity=c)
    else:
        raise NotImplementedError()


def extract_bag(data: np.ndarray, outdict: dict, c: int, bg: int) -> Bag:
    if bg in data and bg != -1:  # add new bg, no color distinction
        mask = (data != bg).astype(int)
        comps, ncomps = _label(mask, c, bg)
    else:
        comps, ncomps = _label(data, c, bg)
    regions = []
    for i in range(1, ncomps + 1):
        xs, ys = np.where(comps == i)
        xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
        regions.append(
            make_region(data[xmin : xmax + 1, ymin : ymax + 1], xmin, ymin, outdict, bg)
        )
    if (
        len(regions) == 0
    ):  # empty region without content, i.e. black square with bg=black
        return Bag(regions=[make_region(data, 0, 0, outdict, bg)], length=1)
    return Bag(regions=regions, length=len(regions))
