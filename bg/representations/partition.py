import numpy as np
from skimage.measure import label

from bg.representations.base_classes import Figure


def partition(x: np.ndarray, lvl: int) -> set[Figure]:
    res = set()
    if lvl == 1:
        for i in range(x.shape[0]):
            for j in range(x.shape[1]):
                res |= {
                    Figure(level=1, x=i, y=j, color=x[i, j], bitmap=np.array([[1]]))
                }
        return res
    if lvl == 2:
        comps, ncomps = label(x, return_num=True, background=-1, connectivity=1)
        for i in range(1, ncomps + 1):
            xs, ys = np.where(comps == i)
            res |= {
                Figure(
                    level=2,
                    x=xs[0],
                    y=ys[0],
                    color=x[xs[0], ys[0]],
                    bitmap=_bitmap(xs, ys),
                )
            }
        return res
    raise NotImplementedError()


# def _get_bg(x: np.ndarray) -> int | None:
#     bc = np.bincount(x.ravel())
#     if len(bc) > 1 and bc[0] == bc[1]:
#         return None
#     return np.argmax(bc)


# def childs_hash(childs, outdict):
#     h = str(hash(str([hash(c) for c in childs])))
#     outdict[h] = childs
#     return h


def _bitmap(xs, ys):
    _xs = xs - min(xs)
    _ys = ys - min(ys)
    bitmap = np.full((max(_xs) + 1, max(_ys) + 1), -1, dtype=int)
    bitmap[_xs, _ys] = 1
    return bitmap


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


#     comps, ncomps = label(data, return_num=True, background=-1, connectivity=1)
#     prims = []
#     for i in range(1, ncomps + 1):
#         xs, ys = np.where(comps == i)
#             shape=str(shape_hash(xs, ys, outdict)),
#             background=str(data[xs, ys][0]),
#             childs=[],
#             childs_hash=childs_hash([], outdict),
#             x=min(xs),
#             y=min(ys),
#         )
#         prims.append(prim)
#     return prims


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
#         shape=str(shape_hash(xs, ys, outdict)),
#         background=str(bg),
#         childs=childs_1,
#         childs_hash=childs_hash(childs_1, outdict),
#         x=0,
#         y=0,
#     )


# def try_split2shape(
# ) -> bool:
#     target_shape = deepcopy(hashes[shape])
#     src_shape = deepcopy(hashes[src.shape])

#     if src_shape.size > target_shape.size:
#         conv = signal.convolve(target_shape, src_shape, mode="valid")
#         area = np.sum(target_shape == 1)
#         _result = []
#         for x, y in zip(*np.where(conv == area)):
#             src_shape[x : x + target_shape.shape[0], y :
# y + target_shape.shape[1]] = -1
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
