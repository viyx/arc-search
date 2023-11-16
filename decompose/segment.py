import numpy as np
from skimage.measure import label

from decompose.primitives import Region

# def _get_bg(x: np.ndarray) -> int | None:
#     bc = np.bincount(x.ravel())
#     if len(bc) > 1 and bc[0] == bc[1]:
#         return None
#     return np.argmax(bc)


def _shape_bitmap(xs, ys):
    _xs = xs - min(xs)
    _ys = ys - min(ys)
    bitmap = np.full((max(_xs) + 1, max(_ys) + 1), -1, dtype=int)
    bitmap[_xs, _ys] = 1
    return bitmap


def shape_hash(xs, ys, outdict):
    bitmap = _shape_bitmap(xs, ys)
    h = hash(str(bitmap))
    outdict[str(h)] = bitmap
    return h


def colored_shape_hash(xs, ys, colors, outdict):
    bitmap = _shape_bitmap(xs, ys)
    _xs, _ys = np.where(bitmap == 1)
    bitmap[_xs, _ys] = colors
    h = hash(str(bitmap))
    outdict[str(h)] = bitmap
    return h


def is_rect(xs: np.ndarray, ys: np.ndarray) -> bool:
    samex = len(set(np.bincount(xs)) - {0}) == 1
    samey = len(set(np.bincount(ys)) - {0}) == 1
    return samex and samey


def extract_primitives(data: np.ndarray, outdict: dict) -> list[Region]:
    comps, ncomps = label(data, return_num=True, background=-1, connectivity=1)
    prims = []
    for i in range(1, ncomps + 1):
        xs, ys = np.where(comps == i)
        prim = Region(
            shape=str(shape_hash(xs, ys, outdict)),
            background=str(data[xs, ys][0]),
            childs=[],
            x=min(xs),
            y=min(ys),
        )
        prims.append(prim)
    return prims


def extract_region_simple(raw: np.ndarray, outdict: dict) -> Region:
    bg = 0
    binary_view = raw != bg
    binary_comps, ncomps = label(
        binary_view, return_num=True, background=bg, connectivity=1
    )
    childs_1 = []
    for i in range(1, ncomps + 1):
        xs, ys = np.where(binary_comps == i)
        one_colored = len(np.unique(raw[xs, ys].ravel())) == 1

        childs_2 = []
        if not one_colored:
            bm = _shape_bitmap(xs, ys)
            bm[xs, ys] = raw[xs, ys]
            childs_2 = extract_primitives(bm, outdict)
        child = Region(
            shape=str(shape_hash(xs, ys, outdict)),
            background=str(raw[xs, ys][0])
            if one_colored
            else str(colored_shape_hash(xs, ys, raw[xs, ys].ravel(), outdict)),
            childs=childs_2,
            x=min(xs),
            y=min(ys),
        )
        childs_1.append(child)

    xs, ys = np.indices(raw.shape).reshape(2, -1)
    return Region(
        shape=str(shape_hash(xs, ys, outdict)),
        background=str(bg),
        childs=childs_1,
        x=0,
        y=0,
    )
