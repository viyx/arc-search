from copy import deepcopy

import numpy as np
from pydantic import BaseModel
from scipy import signal


class Region(BaseModel):
    x: int
    y: int
    background: str
    shape: str
    childs: list["Region"]

    def childs_hash(self) -> str:
        return str(hash(str([hash(c) for c in self.childs])))

    def __hash__(self) -> int:
        return hash(
            str([self.x, self.y, self.shape, self.background, self.childs_hash()])
        )

    def max_level(self) -> int:
        def _max_level(regs: list["Region"], lvl=0) -> int:
            if len(regs) == 0:
                return lvl
            cnts = []
            for r in regs:
                cnts.append(_max_level(r.childs, lvl + 1))
            return max(cnts)

        return _max_level([self])

    def get_level_data(self, level: int) -> list["Region"] | None:
        def _get_level_data(data: list["Region"], lvl: int):
            if lvl == 0:
                return data
            _data = []
            for reg in data:
                _data.extend(_get_level_data(reg.childs, lvl - 1))
            return _data

        return _get_level_data([self], level)

    def convert_shape(self, lgg: dict, hashes: dict):
        # only shape convert
        target = deepcopy(hashes[lgg["shape"]])
        src = deepcopy(hashes[self.shape])

        if src.size > target.size:
            conv = signal.convolve(target, src, mode="valid")
            area = np.sum(target == 1)
            result = []
            for x, y in zip(*np.where(conv == area)):
                src[x : x + target.shape[0], y : y + target.shape[1]] = -1
                if len(self.background) == 1:
                    _bg_hash = self.background
                else:
                    _bg_data = hashes[self.background][
                        x : x + target.shape[0], y : y + target.shape[1]
                    ]
                    _bg_hash = str(hash(str(_bg_data)))
                    hashes[_bg_hash] = _bg_data
                result.append(
                    Region(
                        x=self.x + x,
                        y=self.y + y,
                        background=_bg_hash,
                        shape=lgg["shape"],
                        childs=[],
                    )
                )
            if np.all(src == -1):
                return result
        return [self]

    def render(self, hashes) -> np.ndarray:
        def make_bg(shape, hashes, bg):
            if 0 <= int(bg) < 10:
                r = np.full(hashes[shape].shape, int(bg))
            else:
                r = hashes[bg]
            return r

        reg_main = make_bg(self.shape, hashes, self.background)

        for ch in self.childs:
            data_ch = make_bg(ch.shape, hashes, ch.background)
            if np.any(data_ch == -1):
                raise NotImplementedError("-1 in BG.")
            reg_main[
                ch.x : ch.x + data_ch.shape[0], ch.y : ch.y + data_ch.shape[1]
            ] = data_ch
        return reg_main
