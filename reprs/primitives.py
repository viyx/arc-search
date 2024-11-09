from collections.abc import Sequence
from functools import cached_property
from typing import Any, Hashable

import numpy as np
import pydantic

NO_BG = -1
BG = [NO_BG, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


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

    @pydantic.computed_field  # ??
    @cached_property
    def raw_view(self) -> np.ndarray:
        _r = np.full_like(self.raw, NO_BG)
        _r[self.mask] = self.raw[self.mask]
        return _r

    @property
    def content_dicts(self) -> dict[str, np.ndarray]:
        return {self.color_hash: self.raw_view, self.mask_hash: self.mask}

    @cached_property
    def unq_colors(self) -> list[int]:
        return sorted(set(np.unique(self.raw_view)) - {NO_BG})

    @property
    def is_one_colored(self) -> bool:
        return len(self.unq_colors) == 1

    @cached_property
    def is_rect(self) -> bool:
        return np.all(self.mask)

    @property
    def is_primitive(self) -> bool:
        return self.is_one_colored and self.is_rect

    @pydantic.computed_field
    @property
    def width(self) -> int:
        return self.raw_view.shape[1]

    @pydantic.computed_field
    @property
    def height(self) -> int:
        return self.raw_view.shape[0]

    @classmethod
    def main_props(cls) -> set[str]:
        return {"x", "y"} | cls.content_props()

    @classmethod
    def content_props(cls) -> set[str]:
        return {"color_hash"}

    @classmethod
    def position_props(cls) -> set[str]:
        return {"x", "y"}

    @classmethod
    def size_props(cls) -> set[str]:
        return {"width", "height"}

    def dump_main_props(
        self, *, exclude: set[str] | None = None, include: set[str] | None = None
    ) -> dict:
        incl = self.main_props() | include if include else self.main_props()
        return self.model_dump(include=incl, exclude=exclude)

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
            if NO_BG in np.unique(v):
                raise ValueError(f"Content cannot have {NO_BG}.")
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

    def dump_main_props(
        self, *, exclude: set[str] | None = None, include: set[str] | None = None
    ) -> tuple[dict]:
        return tuple(
            r.dump_main_props(exclude=exclude, include=include) for r in self.regions
        )

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


class TaskBags(pydantic.BaseModel, Hashable):
    x: Sequence[Bag]
    y: Sequence[Bag]
    x_test: Sequence[Bag]
    y_test: Sequence[Bag] | None

    def to_list(self, include_ytest: bool = True) -> list[Sequence[Bag]]:
        if include_ytest and self.y_test:
            return [self.x, self.y, self.x_test, self.y_test]
        return [self.x, self.y, self.x_test]

    @classmethod
    def from_tuples(
        cls, x: tuple[Bag], x_test: tuple[Bag], y: tuple[Bag], y_test: tuple[Bag] | None
    ) -> "TaskBags":
        return cls(x=x, y=y, x_test=x_test, y_test=y_test)

    @classmethod
    def to_dicts(
        cls,
        data: Sequence[Bag],
        *,
        exclude: set[str] | None = None,
        include: set[str] | None = None,
    ) -> tuple[tuple[dict]]:
        return tuple(b.dump_main_props(exclude=exclude, include=include) for b in data)

    def collect_hashes(self):
        res = {}
        for seq in self.to_list(include_ytest=False):
            for b in seq:
                for r in b.regions:
                    res.update(r.content_dicts)
        return res

    @classmethod
    def from_dicts(cls, data: list[list[dict]]) -> list[Bag]:
        res = []
        for b in data:
            regs = []
            for r in b:
                regs.append(Region(**r))
            res.append(Bag(regions=regs))
        return res

    def __hash__(self) -> int:
        return hash(
            str([hash(self.x), hash(self.y), hash(self.x_test), hash(self.y_test)])
        )
