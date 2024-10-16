class Answer:
    def __init__(self, fields: list[str]):
        self._solution = {k: None for k in fields}

    def add_const(self, field: str, value: int | str):
        if field in self._solution:
            self._solution[field] = value

    @property
    def target_fields(self) -> set[str]:
        return {k for k, v in self._solution.items() if v is None}

    @property
    def success(self) -> bool:
        return len(self.target_fields) == 0
