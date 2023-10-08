from __future__ import annotations

from typing import Iterator

import numpy as np
from skimage.measure import label

from datasets.arc import TaskData, TaskLayout

BG = 0


def extract_lines(x: np.ndarray) -> list[dict]:
    colors = set(np.unique(x)) - {BG}
    lines = []
    for color in colors:
        # hlines
        for i in range(x.shape[0]):
            line = (x[i, :] == color).astype(np.uint8)
            labeledl, ncomps = label(line, return_num=True, background=BG)
            if ncomps > 0:
                for comp in range(1, ncomps + 1):
                    _ys, *_ = np.where(label(labeledl) == comp)
                    if len(_ys) == 1:
                        continue
                    lines.append(
                        {"color": color, "pos": (i, _ys[0]), "shape": (1, len(_ys))}
                    )
        # vlines
        for i in range(x.shape[1]):
            line = (x[:, i] == color).astype(np.uint8)
            labeledl, ncomps = label(line, return_num=True, background=BG)
            if ncomps > 0:
                for comp in range(1, ncomps + 1):
                    _xs, *_ = np.where(label(labeledl) == comp)
                    if len(_xs) == 1:
                        continue
                    lines.append(
                        {"color": color, "pos": (_xs[0], i), "shape": (len(_xs), 1)}
                    )
        # dots
        for i in range(x.shape[1]):
            line = (x[:, i] == color).astype(np.uint8)
            labeledl, ncomps = label(line, return_num=True, background=BG)
            if ncomps > 0:
                for comp in range(1, ncomps + 1):
                    _xs, *_ = np.where(label(labeledl) == comp)
                    if len(_xs) == 1:
                        left = np.any(x[_xs[0], i - 1 : i] != color)
                        right = np.any(x[_xs[0], i + 1 : i + 2] != color)
                        if left and right:
                            lines.append(
                                {
                                    "color": color,
                                    "pos": (_xs[0], i),
                                    "shape": (len(_xs), 1),
                                }
                            )
    return lines


class Decomposer(TaskLayout):
    def __init__(self, task: TaskData) -> None:
        self._task = task
        self._result = []

    def decompose(self) -> None:
        comps = []
        for x, y in self._task.train_xy:
            e = {
                "x": {"shape": x.shape, "lines": extract_lines(x)},
                "y": {"shape": y.shape, "lines": extract_lines(y)},
            }
            comps.append(e)
        self._result = comps

    @property
    def train_x(self) -> list:
        return [r["x"]["lines"] for r in self._result]

    @property
    def train_y(self) -> list:
        return [r["y"]["lines"] for r in self._result]

    @property
    def train_xy(self) -> Iterator[tuple]:
        return zip(self.train_x, self.train_y)

    @property
    def test_x(self) -> list:
        return []

    @property
    def test_y(self) -> list | None:
        return []
