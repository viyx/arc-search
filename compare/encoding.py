from datasets.arc import Task


class ComponentAnalyzator:
    def __init__(self, task: Task) -> None:
        self._task = task
