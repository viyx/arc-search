from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Iterator

import numpy as np


class TaskLayout(ABC):
    @property
    @abstractmethod
    def train_x(self) -> list:
        ...

    @property
    @abstractmethod
    def train_y(self) -> list:
        ...

    @property
    @abstractmethod
    def train_xy(self) -> Iterator[tuple]:
        ...

    @property
    @abstractmethod
    def test_x(self) -> list:
        ...

    @property
    @abstractmethod
    def test_y(self) -> list | None:
        ...


class RawTaskData(TaskLayout):
    def __init__(
        self,
        train_x: np.ndarray,
        train_y: np.ndarray,
        test_x: np.ndarray,
        test_y: np.ndarray | None,
    ) -> None:
        self._train_x = train_x
        self._train_y = train_y
        self._test_x = test_x
        self._test_y = test_y

    @property
    def train_x(self) -> list[np.ndarray]:
        return self._train_x

    @property
    def train_y(self) -> list[np.ndarray]:
        return self._train_y

    @property
    def train_xy(self) -> Iterator[tuple[np.ndarray, np.ndarray]]:
        return zip(self._train_x, self.train_y)

    @property
    def test_x(self) -> list[np.ndarray]:
        return self._test_x

    @property
    def test_y(self) -> list[np.ndarray] | None:
        return self._test_y


class ARCDataset:
    def __init__(self, task_files: list[str], on_submition: bool = False) -> None:
        if task_files is None:
            raise ValueError("Specify tasks.")
        if not isinstance(task_files, list):
            raise ValueError("Provide list of tasks.")
        self._task_files = task_files
        self._on_submition = on_submition

    @property
    def task_files(self) -> list[str]:
        return self._task_files

    def __len__(self) -> int:
        return len(self._task_files)

    def __getitem__(self, idx: int) -> RawTaskData:
        if idx >= len(self):
            raise IndexError("Index out of range.")

        filename = self._task_files[idx]
        with open(filename, encoding="utf-8") as raw:
            data = json.load(raw)
            train_x = [np.array(d["input"], dtype="uint8") for d in data["train"]]
            train_y = [np.array(d["output"], dtype="uint8") for d in data["train"]]
            test_x = [np.array(d["input"], dtype="uint8") for d in data["test"]]
            test_y = None
            if not self._on_submition:
                test_y = [np.array(d["output"], dtype="uint8") for d in data["test"]]
            return RawTaskData(train_x, train_y, test_x, test_y)
