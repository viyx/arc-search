import numpy as np
import pytest

from datasets.arc import ARCDataset
from search.go import TaskSearch


@pytest.mark.parametrize(
    "task", ["./data/arc/evaluation/f45f5ca7.json", "./data/arc/training/4258a5f9.json"]
)
def test_wblack_bg(task):
    ds = ARCDataset(task_files=[task])
    xnode = "Reg(-1, 1) --> Prim( 0,-1)"
    ynode = xnode
    s = TaskSearch("", ds[0])
    s.add_priority_nodes(xnode, ynode)
    s.search_topdown()
    assert s.success
    preds = s.test()
    for y, pred in zip(ds[0].test_y, preds):
        assert np.all(y == pred)
