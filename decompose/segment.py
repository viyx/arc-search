import numpy as np
from skimage.morphology import label
from toponetx.classes import CombinatorialComplex as CCC


def shape_bitmap(xs, ys):
    _xs = xs - min(xs)
    _ys = ys - min(ys)
    bitmap = np.full((max(_xs) + 1, max(_ys) + 1), -1, dtype=int)
    bitmap[_xs, _ys] = 1
    return bitmap


def shape_hash(xs, ys):
    bitmap = shape_bitmap(xs, ys)
    return hash(str(bitmap))


def colored_shape_hash(xs, ys, colors):
    bitmap = shape_bitmap(xs, ys)
    _xs, _ys = np.where(bitmap)
    bitmap[_xs, _ys] = colors
    return hash(str(bitmap))


def make_primitives(data: np.ndarray, x, y, bitmap: np.ndarray, rank: int, ccc: CCC):
    bg = -1
    _data = np.full(data.shape, bg)
    xs, ys = np.where(bitmap)
    _data[xs + x, ys + y] = data[xs + x, ys + y]
    comps, ncomps = label(_data, background=bg, connectivity=1, return_num=True)

    for i in range(1, ncomps + 1):
        xs, ys = np.where(comps == i)
        if len(xs) == 1:
            continue
        colors = data[xs, ys]
        vertices = list(zip(xs, ys))
        ch = (
            uc[0]
            if len(uc := np.unique(colors)) == 1
            else colored_shape_hash(xs, ys, colors)
        )
        sh = shape_bitmap(xs, ys)
        bh = shape_hash(xs, ys)
        ccc.add_cell(
            vertices, rank=rank, x=xs[0], y=ys[0], color=ch, bitmap=sh, bitmap_hash=bh
        )


def make_bitmaps(data: np.ndarray) -> CCC:
    ccc = CCC()
    max_rank = 100
    xs, ys = np.indices(data.shape).reshape(2, -1)

    # zero rank vertices
    # for _x, _y in zip(xs, ys):
    #     ccc.add_cell([(_x, _y)], rank=0)

    # max rank grid
    # ccc.add_cell(list(zip(xs, ys, data.ravel())),
    #              rank=max_rank,
    #              width=data.shape[1],
    #              height=data.shape[0],
    #              chash=colored_shape_hash(xs, ys, data.ravel())
    #              )

    bg = 0
    binary = data != bg
    binary_comps, nbinary_comps = label(
        binary, background=bg, connectivity=1, return_num=True
    )
    for i in range(1, nbinary_comps + 1):
        xs, ys = np.where(binary_comps == i)
        if len(xs) == 1:
            continue
        vertices = list(zip(xs, ys))
        sh = shape_bitmap(xs, ys)
        bh = shape_hash(xs, ys)
        ccc.add_cell(
            vertices, rank=max_rank - 1, x=xs[0], y=ys[0], bitmap=sh, bitmap_hash=bh
        )
        make_primitives(data, xs[0], ys[0], sh, max_rank - 2, ccc)
    return ccc
