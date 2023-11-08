from typing import Union

import numpy as np
from pydantic import BaseModel


class BaseRect(BaseModel):
    x: int
    y: int
    width: int
    height: int

    def name(self) -> str:
        return self.__class__.__name__.lower()


class RectPrimitive(BaseRect):
    color: int

    def convert2region(self) -> "Region":
        return Region(
            x=self.x,
            y=self.y,
            width=self.width,
            height=self.height,
            background=None,
            childs=[self],
        )

    def can_split_to_shape(self, width: int, height: int) -> bool:
        return self.height % height == 0 and self.width % width == 0

    def convert_to_shape(self, width: int, height: int) -> list["RectPrimitive"]:
        if not self.can_split_to_shape(width, height):
            raise NotImplementedError()
        xruns = self.height // height
        yruns = self.width // width
        blocks = []

        for i in range(xruns):
            for j in range(yruns):
                x = self.x + i * height
                y = self.y + j * width
                p = RectPrimitive(
                    x=x, y=y, width=width, height=height, color=self.color
                )
                blocks.append(p)
        return blocks


class Region(BaseRect):
    background: int | None
    childs: list[Union["Region", RectPrimitive]]

    def to_numpy(self) -> np.ndarray:
        a = np.full(fill_value=(self.background or -1), shape=(self.height, self.width))
        for c in self.childs:
            if not isinstance(c, RectPrimitive):
                raise NotImplementedError()
            a[c.x : c.x + c.height, c.y : c.y + c.width] = c.color
        return a
