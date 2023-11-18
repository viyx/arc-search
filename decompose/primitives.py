import numpy as np
from pydantic import BaseModel


class Region(BaseModel):
    x: int
    y: int
    background: str
    shape: str
    childs_hash: str
    childs: list["Region"]

    # @computed_field
    # def childs_hash(self) -> str:
    #     return str(hash(str([hash(c) for c in self.childs])))

    def __hash__(self) -> int:
        return hash(
            str([self.x, self.y, self.shape, self.background, self.childs_hash])
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
        if level > self.max_level():
            raise ValueError("Exceed maximum level.")

        def _get_level_data(data: list["Region"], lvl: int):
            if lvl == 0:
                return data
            _data = []
            for reg in data:
                _data.extend(_get_level_data(reg.childs, lvl - 1))
            return _data

        return _get_level_data([self], level)

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
