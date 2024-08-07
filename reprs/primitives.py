from functools import cached_property

import numpy as np
import pydantic


class Region(pydantic.BaseModel):
    x: int
    y: int
    raw: np.ndarray  # [0:10]
    mask: np.ndarray  # [0,-1]

    #
    #  Computed fields:
    #
    #  height: int
    #  width: int
    #  mask_hash: str
    #  raw_view: np.ndarray
    #  raw_view_hash: str

    @pydantic.computed_field
    def width(self) -> int:
        return self.raw.shape[1]

    @pydantic.computed_field
    def height(self) -> int:
        return self.raw.shape[0]

    @pydantic.computed_field
    @cached_property
    def raw_view_hash(self) -> str:
        return str(hash(str(self.raw_view)))

    @pydantic.computed_field
    @cached_property
    def mask_hash(self) -> str:
        return str(hash(str(self.mask)))

    @pydantic.computed_field
    @cached_property
    def raw_view(self) -> np.ndarray:
        _r = np.full_like(self.mask, -1)
        _m = self.mask != -1
        _r[_m] = self.raw[_m]
        return _r

    @property
    def colors(self) -> set[int]:
        return set(sorted(np.unique(self.raw_view))) - {-1}

    @property
    def is_primitive(self) -> bool:
        return len(self.colors) == 1

    @classmethod
    def blank(cls) -> dict:
        # no raw
        return {
            "x": "UND",
            "y": "UND",
            "width": "UND",
            "height": "UND",
            "mask_hash": "UND",
            "raw_view_hash": "UND",
        }

    @property
    def target_fields(self) -> set[str]:
        return self.model_fields_set - {"raw", "mask"}

    def __hash__(self) -> int:
        return hash(
            str(
                [
                    self.x,
                    self.y,
                    self.raw_view_hash,
                ]
            )
        )

    def __eq__(self, value: object) -> bool:
        if isinstance(value, type(self)):
            return hash(value) == hash(self)
        return super().__eq__(value)

    @classmethod
    @pydantic.validator("raw")
    def validate_raw_values(cls, v):
        if v.dtype != "uint8":
            raise ValueError(f"Unsupported type {v.dtype}")
        if -1 in np.unique(v):
            raise ValueError("Content cannot have -1.")

    @classmethod
    @pydantic.validator("mask")
    def validate_mask_values(cls, v):
        if v.dtype != "uint8":
            raise ValueError(f"Unsupported type {v.dtype}")
        unqs = np.unique(v)
        if len(unqs) == 1:
            if unqs[0] == -1:
                raise ValueError("Full mask is not possible.")
        elif len(unqs) == 2:
            if 1 not in unqs or -1 not in unqs:
                raise ValueError("Musk consists only from 0 and -1.")
        else:
            raise ValueError("Musk consists only from 0 and -1.")

    @classmethod
    @pydantic.model_validator(mode="before")
    def check_consistency(cls, data: dict) -> dict:
        if data["mask"].shape != data["raw"].shape:
            raise ValueError("Mask doesn't match with content.")
        return data

    class Config:
        arbitrary_types_allowed = True


class Bag(pydantic.BaseModel):
    regions: list[Region]

    #
    #  Computed fields
    #
    #  length : int

    @pydantic.computed_field
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

    @cached_property
    def all_primitive(self) -> bool:
        return all(r.is_primitive for r in self.regions)

    @cached_property
    def colors(self) -> set[int]:
        return set(sorted(c for r in self.regions for c in r.colors))

    @cached_property
    def shapes(self) -> set[tuple[int, int]]:
        return set(sorted(s for r in self.regions for s in r.shape))

    def __hash__(self) -> int:
        return hash(str(sorted(hash(r) for r in self.regions)))
