import logging
from collections.abc import Sequence
from copy import copy

from reprs.primitives import Region, TaskBags
from search.solvers.base import (
    ConstantsRemover,
    Dictionarizer,
    PrimitiveSolver,
    Solver,
    Transformer,
)
from search.solvers.metafeatures import TaskMetaFeatures
from search.solvers.prolog.aleph import AlephSwipl
from search.solvers.prolog.bg import BASE_BG

SSD = Sequence[Sequence[dict]]


def validate_answer(data: SSD) -> bool:
    poskeys = Region.position_props()
    for x in data:
        grid = {}
        for r in x:
            pos = frozenset((k, v) for k, v in r.items() if k in poskeys)
            _data = set((k, v) for k, v in r.items() if k not in poskeys)
            if pos in grid and grid[pos] != _data:
                return False
            grid[pos] = _data
    return True


# TODO: Cache prediction??, cache transformations
class Pipeline(Solver):
    def __init__(self, tf: TaskMetaFeatures, steps: list[Transformer | Solver]):
        super().__init__(tf)
        self.steps = steps
        self.success_step = None
        self.logger = logging.getLogger("app.pipe")

    def solve(self, x, y):
        raise NotImplementedError()

    def solve_validate(self, x, y, xtest):
        _x, _y, _xtest = copy(x), copy(y), copy(xtest)
        self.logger.debug(
            "Start solving and validation, with %s steps", len(self.steps)
        )
        for i, s in enumerate(self.steps):
            if isinstance(s, Transformer):
                _x, _y = s.fit_transform(_x, _y)
                _xtest = s.transform_xtest(_xtest)
            if isinstance(s, Solver):
                try:
                    if s.solve(_x, _y):
                        _ytest = s.predict(_xtest)
                        if validate_answer(_ytest):
                            self.success = True
                            self.success_step = i
                            return True
                except RuntimeError as e:
                    self.logger.error("Error on step %s in solver %s: %s", i, s, e)
                    continue
                except AttributeError as e:
                    self.logger.error("Error on step %s in solver %s: %s", i, s, e)
                    continue
        return False

    def predict(self, x):
        if not self.success:
            raise AttributeError("The solver has no solution.")
        _x = copy(x)
        for i in range(self.success_step + 1):
            s = self.steps[i]
            if isinstance(s, Transformer):
                _x = s.transform_xtest(_x)
            if isinstance(s, Solver) and i == self.success_step:
                p = s.predict(_x)
                break

        for s in reversed(self.steps[: self.success_step + 1]):
            if isinstance(s, Transformer):
                p = s.inverse_transform_xtest(p)
        return p


def main_pipe(task: TaskBags, *, exclude: set[str] | None = None) -> SSD | None:
    tf = TaskMetaFeatures(task, exclude=exclude)
    if exclude or (tf.all_y_pixels and tf.all_x_pixels):
        pipe_prim = Pipeline(
            tf,
            steps=[
                Dictionarizer(exclude=exclude),
                PrimitiveSolver(tf),
            ],
        )
        if pipe_prim.solve_validate(task.x, task.y, task.x_test):
            return pipe_prim.predict(task.x_test)

        pipe_prolog = Pipeline(
            tf,
            steps=[
                Dictionarizer(exclude=exclude),
                ConstantsRemover(),
                # AlephSwipl(tf, bg=BASE_BG, opt_neg_n=0, timeout=30),
                # AlephSwipl(tf, bg=BASE_BG, opt_neg_n=100, timeout=30),
                # AlephSwipl(tf, bg=BASE_BG, opt_neg_n=1000, timeout=60),
                AlephSwipl(tf, bg=BASE_BG, opt_neg_n=5000, timeout=60),
            ],
        )
        if pipe_prolog.solve_validate(task.x, task.y, task.x_test):
            return pipe_prolog.predict(task.x_test)
    return None
