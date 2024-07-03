import numpy as np
from pydantic import BaseModel, computed_field


class Region(BaseModel):
    x: int
    y: int
    width: int
    height: int
    raw: np.ndarray
    bitmap: np.ndarray
    raw_hash: str
    bitmap_hash: str

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
        return self.model_fields_set - {"raw"}

    # def view(self) -> np.ndarray:
    #     a = np.full_like(self.bitmap, -1)
    #     a

    def __hash__(self) -> int:
        return hash(str([self.x, self.y, self.width, self.height, self.raw_hash]))

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
        return hash(str([hash(r) for r in self.regions]))
