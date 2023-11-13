import typing

from toponetx.classes import CombinatorialComplex as CCC

from datasets.arc import RawTaskData
from decompose.segment import make_topology


def find_mapping(x: list[int], y: list[int]) -> dict | None:
    if len(x) != len(y):
        raise NotImplementedError()

    m = {}
    for _x, _y in zip(x, y):
        if _x in m:
            if not m[_x] == _y:
                return None
            continue
        m[_x] = _y
    return m


def _get_rank_edges(ccc: CCC, rank: int):
    hedges = ccc.cells.hyperedge_dict[rank]
    return hedges


def _substitution(data: list[dict]) -> dict:
    s = data[0]
    s = {k: v for k, v in s.items() if isinstance(v, typing.Hashable)}

    for d in data:
        for a in s:
            if s[a] == d[a]:
                continue
            s[a] = "VAR"
    if "weight" in s:
        del s["weight"]
    return s


def lggs(cells: list[CCC], rank: int) -> list[dict]:
    subs = []
    for ccc in cells:
        hedges = _get_rank_edges(ccc, rank)
        if hedges == {}:
            return None
        sub = _substitution(list(hedges.values()))
        if sub == {}:
            return None
        subs.append(sub)
    return subs
    # sub_pairwise = [_substitution([subs[0], subs[i]]) for i in range(1, len(subs))]
    # return sub_pairwise


class TaskSearch:
    def __init__(self, task: RawTaskData) -> None:
        self.task = task
        self.success = False
        self.steps = []

    def search_topdown(self) -> None:
        xs = [make_topology(x) for x in self.task.train_x]
        ys = [make_topology(x) for x in self.task.train_y]

        for ry in ys[0].ranks[::-1]:
            ylggs = lggs(ys, ry)
            if ylggs is not None:
                for rx in xs[0].ranks[::-1]:
                    xlggs = lggs(xs, rx)
                    if xlggs is not None:
                        self.make_greedy_step()
        print()

    def make_greedy_step(self):
        pass
