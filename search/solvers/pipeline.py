from collections.abc import Sequence
from copy import copy

from reprs.primitives import TaskBags
from reprs.validation import validate_positions
from search.solvers.base import Dictionarizer, PrimitiveSolver, Solver, Transformer
from search.solvers.metafeatures import TaskMetaFeatures
from search.solvers.prolog.aleph import AlephSWI
from search.solvers.prolog.bg import BASE_BG

SSD = Sequence[Sequence[dict]]


#   TODO remove double call of `predict`, remove Solver
#   TODO Cache prediction, cache transformations, move to sklearn api
class Pipeline(Solver):
    def __init__(
        self,
        parent_logger: str,
        tf: TaskMetaFeatures,
        *,
        steps: list[Transformer | Solver],
    ):
        super().__init__(parent_logger, tf)
        self.steps = steps
        self.success_step = None

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
                        if validate_positions(_ytest):
                            self.success = True
                            self.success_step = i
                            return True
                        raise RuntimeError("Validation failed.")
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


#   TODO pass args from cmd, config??
def main_pipe(
    parent_logger: str,
    task: TaskBags,
    **kwargs: dict,
) -> SSD | None:
    tf = TaskMetaFeatures(task, **kwargs)
    if kwargs or (tf.all_y_pixels and tf.all_x_pixels):
        solver1 = PrimitiveSolver(parent_logger, tf)
        solver2 = AlephSWI(parent_logger, tf, bg=BASE_BG, opt_neg_n=5000, timeout=200)
        steps1 = [Dictionarizer(parent_logger, **kwargs), solver1]
        steps2 = [Dictionarizer(parent_logger, **kwargs), solver2]

        for steps in [steps1, steps2]:
            pipe_prolog1 = Pipeline(parent_logger, tf, steps=steps)
            if pipe_prolog1.solve_validate(task.x, task.y, task.x_test):
                return pipe_prolog1.predict(task.x_test)
    return None
