import numpy as np
from pydantic import BaseModel


class Region(BaseModel):
    x: int
    y: int
    width: int
    height: int
    raw: np.ndarray
    raw_hash: str
    # bitmap_hash

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
    def model_hashable_fields(self) -> set[str]:
        return self.model_fields_set - {"raw"}

    def __hash__(self) -> int:
        return hash(str([self.x, self.y, self.width, self.height, self.raw_hash]))

    class Config:
        arbitrary_types_allowed = True


class Bag(BaseModel):
    length: int
    regions: list[Region]

    @property
    def model_hashable_fields(self) -> set[str]:
        return self.model_fields_set

    @classmethod
    def blank(cls) -> dict:
        return {"regions": Region.blank(), "length": "UND"}

    def __hash__(self) -> int:
        return hash(str([hash(r) for r in self.regions]))
