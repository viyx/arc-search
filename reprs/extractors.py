import numpy as np
from skimage.measure import label

from reprs.primitives import Bag, Region

# def _get_bg(x: np.ndarray) -> int | None:
#     bc = np.bincount(x.ravel())
#     if len(bc) > 1 and bc[0] == bc[1]:
#         return None
#     return np.argmax(bc)


# def childs_hash(childs, outdict):
#     h = str(hash(str([hash(c) for c in childs])))
#     outdict[h] = childs
#     return h


# def _shape_bitmap(xs, ys):
#     _xs = xs - min(xs)
#     _ys = ys - min(ys)
#     bitmap = np.full((max(_xs) + 1, max(_ys) + 1), -1, dtype=int)
#     bitmap[_xs, _ys] = 1
#     return bitmap


# def shape_hash(xs, ys, outdict):
#     bitmap = _shape_bitmap(xs, ys)
#     h = hash(str(bitmap))
#     outdict[str(h)] = bitmap
#     return h


# def colored_shape_hash(xs, ys, colors, outdict):
#     bitmap = _shape_bitmap(xs, ys)
#     _xs, _ys = np.where(bitmap == 1)
#     bitmap[_xs, _ys] = colors
#     h = hash(str(bitmap))
#     outdict[str(h)] = bitmap
#     return h


# def is_rect(xs: np.ndarray, ys: np.ndarray) -> bool:
#     samex = len(set(np.bincount(xs)) - {0}) == 1
#     samey = len(set(np.bincount(ys)) - {0}) == 1
#     return samex and samey


def _flatten_and_hash(data: np.ndarray, bg: int) -> str:
    flatten = data.flatten()
    one_colored = len(np.unique(flatten)) == 1
    if one_colored:
        return str(data[0, 0])

    _xs, *_ = np.where(flatten == bg)
    flatten[_xs] = -1
    return str(hash(str(flatten)))


def extract_region(data: np.ndarray, outdict: dict, bg: int) -> Region:
    r = Region(
        x=0,
        y=0,
        raw_hash=_flatten_and_hash(data, bg),
        height=data.shape[0],
        width=data.shape[1],
        raw=data,
    )
    if len(r.raw_hash) > 1:
        outdict[r.raw_hash] = data
    return r


def extract_bag(data: np.ndarray, outdict: dict, bg: int) -> Bag:
    mask = data != bg
    comps, ncomps = label(mask, return_num=True, background=bg, connectivity=1)
    regions = []
    for i in range(1, ncomps + 1):
        xs, ys = np.where(comps == i)
        xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
        regions.append(
            extract_region(data[xmin : xmax + 1, ymin : ymax + 1], outdict, bg)
        )
    return Bag(regions=regions, length=len(regions))


# def extract_primitives(data: np.ndarray, outdict: dict) -> list[Region]:
#     comps, ncomps = label(data, return_num=True, background=-1, connectivity=1)
#     prims = []
#     for i in range(1, ncomps + 1):
#         xs, ys = np.where(comps == i)
#         prim = Region(
#             shape=str(shape_hash(xs, ys, outdict)),
#             background=str(data[xs, ys][0]),
#             childs=[],
#             childs_hash=childs_hash([], outdict),
#             x=min(xs),
#             y=min(ys),
#         )
#         prims.append(prim)
#     return prims


# def extract_hierarchy(raw: np.ndarray, outdict: dict) -> Region:
#     bg = 0
#     binary_view = raw != bg
#     binary_comps, ncomps = label(
#         binary_view, return_num=True, background=bg, connectivity=1
#     )
#     childs_1 = []
#     for i in range(1, ncomps + 1):
#         xs, ys = np.where(binary_comps == i)
#         one_colored = len(np.unique(raw[xs, ys].ravel())) == 1

#         bm = _shape_bitmap(xs, ys)
#         _xs, _ys = np.where(bm == 1)
#         bm[_xs, _ys] = raw[xs, ys]
#         childs_2 = extract_primitives(bm, outdict)
#         child = Region(
#             shape=str(shape_hash(xs, ys, outdict)),
#             background=str(raw[xs, ys][0])
#             if one_colored
#             else str(colored_shape_hash(xs, ys, raw[xs, ys].ravel(), outdict)),
#             childs=childs_2,
#             childs_hash=childs_hash(childs_2, outdict),
#             x=min(xs),
#             y=min(ys),
#         )
#         childs_1.append(child)

#     xs, ys = np.indices(raw.shape).reshape(2, -1)
#     return Region(
#         shape=str(shape_hash(xs, ys, outdict)),
#         background=str(bg),
#         childs=childs_1,
#         childs_hash=childs_hash(childs_1, outdict),
#         x=0,
#         y=0,
#     )


# def try_split2shape(
#     src: Region, shape: str, hashes: dict, result: list["Region"]
# ) -> bool:
#     target_shape = deepcopy(hashes[shape])
#     src_shape = deepcopy(hashes[src.shape])

#     if src_shape.size > target_shape.size:
#         conv = signal.convolve(target_shape, src_shape, mode="valid")
#         area = np.sum(target_shape == 1)
#         _result = []
#         for x, y in zip(*np.where(conv == area)):
#             src_shape[x : x + target_shape.shape[0], y : y +
# target_shape.shape[1]] = -1
#             if len(src.background) == 1:
#                 _bg_hash = src.background
#                 childs = []
#             else:
#                 _bg_data = hashes[src.background][
#                     x : x + target_shape.shape[0], y : y + target_shape.shape[1]
#                 ]
#                 _bg_hash = str(hash(str(_bg_data)))
#                 hashes[_bg_hash] = _bg_data
#                 childs = extract_primitives(_bg_data, hashes)
#             _result.append(
#                 Region(
#                     x=src.x + x,
#                     y=src.y + y,
#                     background=_bg_hash,
#                     shape=shape,
#                     childs=childs,
#                     childs_hash=childs_hash(childs, hashes),
#                 )
#             )
#         if np.all(src_shape == -1):
#             result.extend(_result)
#             return True
#     return False
