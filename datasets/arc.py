from __future__ import annotations

import json

import numpy as np


class Task:
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
    def test_x(self) -> list[np.ndarray]:
        return self._test_x

    @property
    def test_y(self) -> list[np.ndarray] | None:
        return self._test_y


class ARCDataset:
    def __init__(
        self,
        task_files: list[str],
    ) -> None:
        if task_files is None:
            raise ValueError("Specify tasks.")
        if not isinstance(task_files, list):
            raise ValueError("Provide list of tasks.")
        self._task_files = task_files

    @property
    def task_files(self) -> list[str]:
        return self._task_files

    def __len__(self) -> int:
        return len(self._task_files)

    def __getitem__(self, idx: int) -> Task:
        assert idx < len(self), "Index out of range"

        filename = self._task_files[idx]
        with open(filename, encoding="utf-8") as raw:
            data = json.load(raw)
            train_x = list(map(lambda d: np.array(d["input"]), data["train"]))
            train_y = list(map(lambda d: np.array(d["output"]), data["train"]))
            test_x = list(map(lambda d: np.array(d["input"]), data["test"]))
            test_y = None
            if "output" in data["test"][-1]:
                test_y = list(map(lambda d: np.array(d["output"]), data["test"]))
            return Task(train_x, train_y, test_x, test_y)
