from collections.abc import Sequence
from copy import copy

from reprs.primitives import TaskBags
from search.solvers.base import (
    ConstantsRemover,
    Dictionarizer,
    PrimitiveSolver,
    Solver,
    Transformer,
)
from search.solvers.metafeatures import TaskMetaFeatures
from search.solvers.prolog.aleph import Aleph
from search.solvers.prolog.bg import BASE_BG

SSD = Sequence[Sequence[dict]]


class Pipeline(Solver):
    def __init__(self, tf: TaskMetaFeatures, steps: list[Transformer | Solver]):
        super().__init__(tf)
        self.steps = steps
        self.success_step = None

    def solve(self, x, y):
        _x, _y = copy(x), copy(y)
        for i, s in enumerate(self.steps):
            if isinstance(s, Transformer):
                _x, _y = s.fit_transform(_x, _y)
            if isinstance(s, Solver):
                s.solve(_x, _y)
                if s.success:
                    self.success = True
                    self.success_step = i
                    return True
        return False

    def predict(self, x):
        if not self.success:
            raise AttributeError("The solver has no solution.")
        _x = copy(x)
        for i in range(self.success_step + 1):
            s = self.steps[i]
            if isinstance(s, Transformer):
                _x = s.transform_xtest(_x)
            if isinstance(s, Solver):
                if s.success:
                    p = s.predict(_x)
                    break

        for s in reversed(self.steps[: self.success_step + 1]):
            if isinstance(s, Transformer):
                p = s.inverse_transform_xtest(p)
        return p


def solve_pipe(task: TaskBags, *, exclude: set[str] | None = None) -> SSD | None:
    tf = TaskMetaFeatures(task, exclude=exclude)
    if exclude or (tf.all_y_pixels and tf.all_x_pixels):
        pipe = Pipeline(
            tf,
            steps=[
                Dictionarizer(exclude=exclude),
                PrimitiveSolver(tf),
                ConstantsRemover(),
                Aleph(tf, bg=BASE_BG),
            ],
        )
        if pipe.solve(task.x, task.y):
            return pipe.predict(task.x_test)
    return None
