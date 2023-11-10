import numpy as np
from skimage.measure import label

from decompose.primitives import Region


def _get_bg(x: np.ndarray) -> int | None:
    bc = np.bincount(x.ravel())
    if len(bc) > 1 and bc[0] == bc[1]:
        return None
    return np.argmax(bc)


def is_rect(xs: np.ndarray, ys: np.ndarray) -> bool:
    samex = len(set(np.bincount(xs)) - {0}) == 1
    samey = len(set(np.bincount(ys)) - {0}) == 1
    return samex and samey

    # def extract_only_primitives(
    #     x: np.ndarray, only_pixels: bool = False
    # ) -> list[RectPrimitive]:
    #     bg = _get_bg(x)
    #     if only_pixels:
    #         return _extract_pixels(x, bg)
    #     hlines = _extract_hlines(x, bg)
    #     vlines = _extract_vlines(x, bg)
    #     pixels = _extract_solo_pixels(x, bg)
    #     return [*hlines, *vlines, *pixels]

    # def _extract_hlines(x: np.ndarray, bg: int | None) -> list[dict]:
    # colors = set(np.unique(x)) - {bg}
    # lines = []
    # for color in colors:
    #     for i in range(x.shape[0]):
    #         line = (x[i, :] == color).astype(np.uint8)
    #         labeledl, ncomps = label(line, return_num=True, background=bg)
    #         if ncomps > 0:
    #             for comp in range(1, ncomps + 1):
    #                 _ys, *_ = np.where(label(labeledl) == comp)
    #                 if len(_ys) == 1:
    #                     continue
    #                 lines.append(
    #                     RectPrimitive(
    #                         color=color,
    #                         position=(i, _ys[0]),
    #                         shape=(1, len(_ys)),
    #                     )
    #                 )
    # return lines

    # def _extract_vlines(x: np.ndarray, bg: int | None) -> list[dict]:
    # colors = set(np.unique(x)) - {bg}
    # lines = []
    # for color in colors:
    #     for i in range(x.shape[1]):
    #         line = (x[:, i] == color).astype(np.uint8)
    #         labeledl, ncomps = label(line, return_num=True, background=bg)
    #         if ncomps > 0:
    #             for comp in range(1, ncomps + 1):
    #                 _xs, *_ = np.where(label(labeledl) == comp)
    #                 if len(_xs) == 1:
    #                     continue
    #                 lines.append(
    #                     RectPrimitive(
    #                         color=color,
    #                         position=(_xs[0], i),
    #                         shape=(len(_xs), 1),
    #                     )
    #                 )
    # return lines

    # def _extract_solo_pixels(x: np.ndarray, bg: int | None) -> list[dict]:
    # colors = set(np.unique(x)) - {bg}
    # pixels = []
    # for color in colors:
    #     for i in range(x.shape[1]):
    #         line = (x[:, i] == color).astype(np.uint8)
    #         labeledl, ncomps = label(line, return_num=True, background=bg)
    #         if ncomps > 0:
    #             for comp in range(1, ncomps + 1):
    #                 _xs, *_ = np.where(label(labeledl) == comp)
    #                 if len(_xs) == 1:
    #                     left = np.any(x[_xs[0], i - 1 : i] != color)
    #                     right = np.any(x[_xs[0], i + 1 : i + 2] != color)
    #                     if left and right:
    #                         pixels.append(
    #                             RectPrimitive(
    #                                 color=color, position=(_xs[0], i), shape=(1, 1)
    #                             )
    #                         )
    # return pixels

    # def _extract_pixels(x: np.ndarray, bg: int | None) -> list[dict]:
    # colors = set(np.unique(x)) - {bg}
    # pixels = []
    # for color in colors:
    #     iis, js = np.where(x == color)
    #     for i, j in zip(iis, js):
    #         pixels.append(RectPrimitive(color=color, position=(i, j), shape=(1, 1)))
    # return pixels


# def extract_topdown(
#     x: np.ndarray, p: tuple[int, int, int, int] | None = None
# ) -> Region | RectPrimitive:
#     if p is None:  # all area
#         p = (0, 0, *x.shape)
#     reg = x[slice(p[0], p[2]), slice(p[1], p[3])]

#     if len(np.unique(reg)) == 1:  # implicit rect
#         prim = RectPrimitive(
#             width=reg.shape[1], height=reg.shape[0], color=reg[0, 0], x=p[0], y=p[1]
#         )
#         return prim

#     bg = _get_bg(reg)
#     childs = []

#     if bg is not None:
#         binary = (reg == bg).astype(int)
#         lbls, ncomps = label(binary, return_num=True, background=1, connectivity=1)
#     else:
#         lbls, ncomps = label(reg, return_num=True, background=None, connectivity=1)
#     for i in range(1, ncomps + 1):
#         xs, ys = np.where(lbls == i)
#         if is_rect(xs, ys):
#             _x0 = p[0] + xs[0]
#             _y0 = p[1] + ys[0]
#             _xn = p[0] + xs[0] + len(np.unique(xs))
#             _yn = p[1] + ys[0] + len(np.unique(ys))
#             newp = (_x0, _y0, _xn, _yn)
#             child = extract_topdown(x, newp)
#             childs.append(child)
#         else:
#             _x0 = p[0] + min(xs)
#             _y0 = p[1] + min(ys)
#             _xn = max(xs) - _x0
#             _yn = max(ys) - _y0

#     return Region(
#         width=reg.shape[1],
#         height=reg.shape[0],
#         background=bg,
#         childs=childs,
#         x=p[0],
#         y=p[1],
#     )


def extract_region_simple(raw: np.ndarray) -> Region:
    bg = _get_bg(raw)
    binary_view = (raw != bg).astype(int)
    binary_comps, ncomps = label(
        binary_view, return_num=True, background=bg, connectivity=1
    )
    childs = []
    for i in range(1, ncomps + 1):
        xs, ys = np.where(binary_comps == i)
        one_colored = len(np.unique(raw[xs, ys].ravel())) == 1
        if is_rect(xs, ys) and one_colored:
            child = Region(
                width=len(np.unique(xs)),
                height=len(np.unique(ys)),
                background=raw[xs, ys][0],
                childs=[],
                x=xs[0],
                y=ys[0],
            )
        else:
            child = Region(
                width=max(ys) - ys[0],
                height=max(xs) - xs[0],
                background=raw[xs[0] : max(xs) + 1, ys[0] : max(ys) + 1],
                childs=[],
                x=xs[0],
                y=ys[0],
            )
        childs.append(child)

    return Region(
        width=raw.shape[1],
        height=raw.shape[0],
        background=bg,
        childs=childs,
        x=0,
        y=0,
    )
