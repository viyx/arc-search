import numpy as np
import pytest

from datasets.arc import ARCDataset
from search.actions import Action, Extractors
from search.go import TaskSearch


@pytest.mark.parametrize(
    "task", ["./data/arc/evaluation/f45f5ca7.json", "./data/arc/training/4258a5f9.json"]
)
def test(task):
    ds = ARCDataset(task_files=[task])
    action = Action(name=Extractors.EP, bg=0, c=-1)
    s = TaskSearch("", ds[0])
    s.init()
    xs = s._add_nodes(
        s.xdag, {action}, s.xdag.init_node, *s.xdag.get_data(s.xdag.init_node)
    )
    ys = s._add_nodes(
        s.ydag, {action}, s.ydag.init_node, *s.ydag.get_data(s.ydag.init_node)
    )
    s._put(
        {s.xdag.init_node},
        {s.ydag.init_node},
        hard_dist=-1,
    )
    s._put(xs, ys, hard_dist=-1)
    s.search_topdown()
    assert s.success
    preds = s.test()
    for y, pred in zip(ds[0].test_y, preds):
        assert np.all(y == pred)
