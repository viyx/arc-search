from collections.abc import Sequence
from functools import cached_property
from typing import Any, Hashable

import numpy as np
import pydantic


class Region(pydantic.BaseModel, Hashable):
    x: int
    y: int
    raw: np.ndarray  # [0:10]
    mask: np.ndarray  # [True, False]

    #
    #  Computed fields:
    #

    #  raw_view: np.ndarray
    #  mask_hash: str
    #  color_hash: str

    @pydantic.computed_field
    @cached_property
    def color_hash(self) -> str:
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
    def unq_colors(self) -> list[int]:
        return sorted(set(np.unique(self.raw_view)) - {-1})

    @property
    def is_one_colored(self) -> bool:
        return len(self.unq_colors) == 1

    @cached_property
    def is_rect(self) -> bool:
        return np.all(self.mask)

    @property
    def is_primitive(self) -> bool:
        return self.is_one_colored and self.is_rect

    @classmethod
    def main_props(cls) -> set[str]:
        return {"x", "y"} | cls.shortcuts_props()

    @classmethod
    def shortcuts_props(cls) -> set[str]:
        return {"mask_hash", "color_hash"}

    def dump_main_props(self) -> dict:
        return self.model_dump(include=self.main_props())

    def __hash__(self) -> int:
        return hash(
            str(
                [
                    self.x,
                    self.y,
                    self.mask_hash,
                    self.color_hash,
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
            if v.dtype != "int8":
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

    class Config:
        arbitrary_types_allowed = True


class Bag(pydantic.BaseModel, Hashable):
    regions: Sequence[Region]

    # def __getitem__(self, i: int):
    #     return self.regions[i]

    # def __len__(self):
    #     return len(self.regions)

    # def __iter__(self):
    #     self._it = 0
    #     return self

    # def __next__(self):
    #     if self._it < len(self) - 1:
    #         self._it += 1
    #         return self[self._it]
    #     raise StopIteration

    @classmethod
    def merge(cls, bags: list["Bag"]) -> "Bag":
        regions = []
        for b in bags:
            regions.extend(b.regions)
        return Bag(regions=tuple(regions))

    def dump_main_props(self) -> tuple[dict]:
        return tuple(r.dump_main_props() for r in self.regions)

    def is_empty(self) -> bool:
        return len(self.regions) == 0

    @cached_property
    def all_one_colored(self) -> bool:
        return all(r.is_one_colored for r in self.regions)

    @cached_property
    def all_pixels(self) -> bool:
        return all(r.mask.shape == (1, 1) for r in self.regions)

    @cached_property
    def all_rect(self) -> bool:
        return all(r.is_rect for r in self.regions)

    @cached_property
    def unq_colors(self) -> list[int]:
        return sorted(set(c for r in self.regions for c in r.unq_colors))

    @cached_property
    def soup_of_props(self) -> set[Any]:
        props = set()
        for r in self.regions:
            props |= set(r.dump_main_props().values())
        return props

    def __hash__(self) -> int:
        return hash(self.regions)


# class BBag(pydantic.BaseModel):
#     bags: Sequence[Bag]

# @cached_property
# def all_primitive(self) -> bool:
#     return all(b.all_primitive for b in self.bags)

# @cached_property
# def unq_colors(self) -> set[str]:
#     s = set()
#     for b in self.bags:
#         s |= b.unq_colors
#     return s

# @cached_property
# def unq_masks(self) -> set[str]:
#     s = set()
#     for b in self.bags:
#         s |= {r.mask_hash for r in b.regions}
#     return s

# @cached_property
# def all_rect(self) -> bool:
#     return all(b.all_rect for b in self.bags)

# @property
# def all_ordinary(self) -> bool:
#     return all(len(b.regions) == 1 for b in self.bags)

# def __hash__(self) -> int:
#     return hash(str([hash(b) for b in self.bags]))


# class TaskContainer(pydantic.BaseModel, abc.ABC):
#     x: Sequence[Sequence]
#     y: Sequence[Sequence]
#     x_test: Sequence[Sequence]
#     y_test: Sequence[Sequence] | None


class TaskBags(pydantic.BaseModel, Hashable):
    x: Sequence[Bag]
    y: Sequence[Bag]
    x_test: Sequence[Bag]
    y_test: Sequence[Bag] | None

    # def __getitem__(self, index: int) -> Sequence[Bag]:
    #     if index == 0:
    #         return self.x
    #     if index == 1:
    #         return self.y
    #     if index == 2:
    #         return self.x_test
    #     if index == 3 and self.y_test is not None:
    #         return self.y_test
    #     raise IndexError()

    # def __len__(self) -> int:
    #     if self.y_test is None:
    #         return 3
    #     return 4

    @property
    def all_bags(self) -> list[Sequence[Bag]]:
        if self.y_test is not None:
            return [self.x, self.y, self.x_test, self.y_test]
        return [self.x, self.y, self.x_test]

    @classmethod
    def from_tuple(
        cls, x: tuple[Bag], y: tuple[Bag], x_test: tuple[Bag], y_test: tuple[Bag] | None
    ) -> "TaskBags":
        return cls(x=x, y=y, x_test=x_test, y_test=y_test)

    @classmethod
    def to_dicts(cls, data: Sequence[Bag]) -> Any:
        return tuple(b.dump_main_props() for b in data)

    def __hash__(self) -> int:
        return hash(
            str([hash(self.x), hash(self.y), hash(self.x_test), hash(self.y_test)])
        )
