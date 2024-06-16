import numpy as np
from pydantic import BaseModel


class Region(BaseModel):
    x: int
    y: int
    width: int
    height: int
    content_hash: str
    content: np.ndarray

    def __hash__(self) -> int:
        return hash(str([self.x, self.y, self.width, self.height, self.content_hash]))

    class Config:
        arbitrary_types_allowed = True


class Bag(BaseModel):
    regions: list[Region]

    def __hash__(self) -> int:
        return hash(str([hash(r) for r in self.regions]))
