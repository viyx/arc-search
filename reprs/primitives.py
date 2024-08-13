from collections import defaultdict
from functools import cached_property
from typing import Any

import numpy as np
import pydantic


class Region(pydantic.BaseModel):
    x: int
    y: int
    raw: np.ndarray  # [0:10]
    mask: np.ndarray  # [True, False]

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
        _r = np.full_like(self.raw, -1)
        _r[self.mask] = self.raw[self.mask]
        return _r

    @cached_property
    def unq_colors(self) -> set[int]:
        return set(np.unique(self.raw_view)) - {-1}

    @property
    def is_primitive(self) -> bool:
        return len(self.unq_colors) == 1

    @classmethod
    def blank(cls) -> dict:
        raise NotImplementedError()
        # no raw
        # return {
        #     "x": "UND",
        #     "y": "UND",
        #     "width": "UND",
        #     "height": "UND",
        #     "mask_hash": "UND",
        #     "raw_view_hash": "UND",
        # }

    @property
    def target_fields(self) -> set[str]:
        return self.model_fields_set - {"raw", "mask"}

    @cached_property
    def all_props(self) -> set[Any]:
        return set(
            [
                self.x,
                self.y,
                self.width,
                self.height,
                self.mask_hash,
                self.raw_view_hash,
            ]
        )

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

    @pydantic.field_validator("raw")
    @classmethod
    def validate_raw_values(cls, v: Any) -> Any:
        if isinstance(v, np.ndarray):
            if v.dtype != "uint8":
                raise ValueError(f"Unsupported type {v.dtype}.")
            if -1 in np.unique(v):
                raise ValueError("Content cannot have -1.")
            return v
        raise ValueError(f"Unsupported type {type(v)}.")

    @pydantic.field_validator("mask")
    @classmethod
    def validate_mask_values(cls, v: Any) -> Any:
        if isinstance(v, np.ndarray):
            if v.dtype != "bool":
                raise ValueError(f"Unsupported type {v.dtype}")
            return v
        raise ValueError(f"Unsupported type {type(v)}.")

    @pydantic.model_validator(mode="before")
    @classmethod
    def check_consistency(cls, data: Any) -> dict:
        if isinstance(data, dict):
            if data["mask"].shape != data["raw"].shape:
                raise ValueError("Mask doesn't match with content.")
            return data
        raise NotImplementedError()

    # def pseudo_entropy(self) -> float:
    #     bm = self.mask_binary
    #     maskp = bm / bm.size
    #     maskent = maskp * np.log2(maskp)
    #     raw_ent = 0
    #     if not self.is_primitive:
    #         flat = self.raw_view[bm].flatten()
    #         np.bincount
    #         self.colors
    #
    # return maskent + raw_ent

    class Config:
        arbitrary_types_allowed = True


class Bag(pydantic.BaseModel):
    regions: list[Region]

    #
    #  Computed fields
    #
    #  length : int

    @pydantic.computed_field
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
    def unq_colors(self) -> set[int]:
        return set(c for r in self.regions for c in r.unq_colors)

    @cached_property
    def soup_of_props(self) -> set[Any]:
        props = set()
        for r in self.regions:
            props |= r.all_props
        return props

    @cached_property
    def get_attr(self, name: str) -> list[Any]:
        return [getattr(r, name) for r in self.regions]

    def __hash__(self) -> int:
        "Hash is indifferent to order of regions."
        return hash(str(sorted(hash(r) for r in self.regions)))


class BBag(pydantic.BaseModel):
    bags: list[Bag]

    @classmethod
    def get_hash(cls, bags: list[Bag]) -> int:
        "Hash is sensitive to order of bags."
        return hash(str([hash(b) for b in bags]))

    def __hash__(self) -> int:
        "Hash is sensitive to order of bags."
        return self.get_hash(self.bags)


class TaskBag(pydantic.BaseModel):
    x: BBag
    y: BBag
    test: BBag

    @classmethod
    def from_tuple(cls, data: tuple[BBag, BBag, BBag]) -> "TaskBag":
        return cls(x=data[0], y=data[1], test=data[2])

    def __hash__(self) -> int:
        return hash(str([hash(self.x), hash(self.y), hash(self.test)]))

    def xyup2(self) -> dict:
        f1 = defaultdict(list)
        for _x, _y in zip(self.x.bags, self.y.bags):
            c1 = len(_x) == len(_y)
            f1["length"].append(c1)
            if c1:
                cx = _x.get_attr("x") == _y.get_attr("x")
                cy = _x.get_attr("y") == _y.get_attr("y")
                cm = _x.get_attr("mask_hash") == _y.get_attr("mask_hash")
                cr = _x.get_attr("raw_view_hash") == _y.get_attr("raw_view_hash")
                f1["x"].append(cx)
                f1["y"].append(cy)
                f1["mask_hash"].append(cm)
                f1["raw_view_hash"].append(cr)
        return f1
