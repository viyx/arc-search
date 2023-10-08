import numpy as np
from skimage.measure import label


def convolve(x: np.ndarray, y: np.ndarray, **kwargs):
    yh, yw = y.shape
    ytopol = label(y, **kwargs)
    out_h = x.shape[0] - yh + 1
    out_w = x.shape[1] - yw + 1
    out = np.zeros((out_h, out_w))
    for i in range(out_h):
        for j in range(out_w):
            xtopol = label(x[i : i + yh, j : j + yw], **kwargs)
            out[i, j] = np.all(xtopol == ytopol)
    return out
