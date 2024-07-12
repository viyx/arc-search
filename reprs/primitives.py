import numpy as np
from pydantic import BaseModel, computed_field


class Region(BaseModel):
    x: int
    y: int
    width: int
    height: int
    raw: np.ndarray
    bitmap: np.ndarray
    # raw_hash: str  - computable
    # bitmap_hash: str - computable
    # raw_view: str - computable

    @computed_field
    @property
    def raw_hash(self) -> str:
        _r = self.raw_view
        unqs = np.unique(_r)
        if len(unqs) == 1:
            if unqs[0] == -1:
                return "-1"
            return str(unqs[0])
        return str(hash(str([_r.flatten(), self.height, self.width])))

    @computed_field
    @property
    def bitmap_hash(self) -> str:
        unqs = np.unique(self.bitmap)
        if len(unqs) == 1 and unqs[0] == -1:
            return "-1"
        return str(hash(str([self.bitmap.flatten(), self.height, self.width])))

    @computed_field
    @property
    def raw_view(self) -> np.ndarray:
        _r = np.full_like(self.bitmap, -1)
        _m = self.bitmap != -1
        _r[_m] = self.raw[_m]
        return _r

    @classmethod
    def blank(cls) -> dict:
        # no raw
        return {
            "x": "UND",
            "y": "UND",
            "width": "UND",
            "height": "UND",
            "raw_hash": "UND",
        }

    @property
    def target_fields(self) -> set[str]:
        return self.model_fields_set - {"raw", "bitmap"}

    def __hash__(self) -> int:
        return hash(
            str(
                [
                    # self.x,
                    # self.y,
                    self.width,
                    self.height,
                    self.raw_hash,
                    self.bitmap_hash,
                ]
            )
        )

    class Config:
        arbitrary_types_allowed = True


class Bag(BaseModel):
    regions: list[Region]

    @computed_field
    @property
    def length(self) -> int:
        return len(self.regions)

    @property
    def target_fields(self) -> set[str]:
        return self.model_fields_set

    @classmethod
    def blank(cls) -> dict:
        return {"regions": Region.blank(), "length": "UND"}

    @classmethod
    def merge(cls, bags: list["Bag"]) -> "Bag":
        regions = []
        for b in bags:
            regions.extend(b.regions)
        return Bag(regions=regions)

    def __hash__(self) -> int:
        return hash(str(sorted(hash(r) for r in self.regions)))
