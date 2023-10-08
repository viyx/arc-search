from __future__ import annotations

import numpy as np


class LinearAnalyzer:
    @staticmethod
    def has_obj_count_dep(
        xs: list[list], ys: list[list]
    ) -> tuple[bool, np.ndarray or None]:
        solutions = []
        for x, y in zip(xs, ys):
            x = np.array([[len(x)]])
            y = np.array([[len(y)]])
            solutions.append(np.linalg.solve(x, y))
        has_unq_sol = len(np.unique(np.vstack(solutions))) == 1
        sol = solutions[0] if has_unq_sol else None
        return has_unq_sol, sol
