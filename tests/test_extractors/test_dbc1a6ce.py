from functools import partial
from itertools import product

import pytest

from datasets.arc import ARCDataset, RawTaskData
from reprs.extractors import extract_prims, extract_regions
from reprs.primitives import TaskBags
from search.actions import Action, Extractors
from search.actions import extract_flat as ef


# task: 'connect dots with lines'
# https://neoneye.github.io/arc/edit.html?dataset=ARC&task=dbc1a6ce
@pytest.fixture(name="raw")
def task1() -> RawTaskData:
    ds = ARCDataset(["./data/arc/training/dbc1a6ce.json"])
    return ds[0]


@pytest.fixture(name="init_action")
def action1() -> Action:
    return Action(name=Extractors.ER, bg=-1, c=1)


@pytest.fixture(name="task")
def task1_bags(raw: RawTaskData, init_action: Action) -> TaskBags:
    xs = tuple(init_action(x) for x in raw.train_x)
    ys = tuple(init_action(x) for x in raw.train_y)
    xtests = tuple(init_action(x) for x in raw.test_x)
    ytests = tuple(init_action(x) for x in raw.test_y)
    taskbags = TaskBags.from_tuples(xs, xtests, ys, ytests)
    return taskbags


@pytest.fixture(name="all_actions")
def actions_0() -> set[Action]:
    res = set()
    bgs = [-1, 0]
    cs = [-1, 1, 2]
    for b, c in product(bgs, cs):
        res.add(Action(name=Extractors.ER, bg=b, c=c))
        res.add(Action(name=Extractors.EP, bg=b, c=c))
    assert len(bgs) * len(cs) * 2 == len(res)
    return res


def test_extract(raw: RawTaskData):
    data = [raw.train_x, raw.train_y, raw.test_x, raw.test_y]
    for d in data:
        for x in d:
            pixels1 = extract_regions(x, -1, -1)
            # assert len(pixels1.regions) == len(pixels1)
            assert pixels1.all_pixels
            assert pixels1.all_rect
            assert pixels1.all_one_colored
            assert len(pixels1.regions) == x.size

            pixels2 = extract_prims(x, -1, -1)
            assert len(pixels1.regions) == len(pixels2.regions)
            assert hash(pixels2) == hash(pixels1)

            # full1 = extract_regions(x, 1, -1)
            # assert len(full1.regions) == 1
            # assert full1.regions[0].is_rect
            # assert not full1.regions[0].is_primitive
            # full12 = extract_regions(x, 2, -1)
            # assert hash(full1) == hash(full12)

            # data2 = extract_prims(x, 1, -1)
            # assert hash(full1.regions) != hash(data2)


def test_actions_redundancy(task: TaskBags, all_actions: set[Action]):
    for bags in task.to_list():
        s = set()
        for a in all_actions:
            s.add(ef(a, bags))
        assert len(s) < len(all_actions)


def test_disconnected(task: TaskBags):
    no_bg = -1
    fake_bg = 10  # fake_bg equals no_bg  in extraction
    a1 = Action(name=Extractors.EP, bg=no_bg, c=-1)
    a2 = Action(name=Extractors.ER, bg=no_bg, c=-1)
    a3 = Action(name=Extractors.ER, bg=fake_bg, c=-1)
    a4 = Action(name=Extractors.EP, bg=fake_bg, c=-1)

    for bags in task.to_list():
        # s = set()
        for a in [a1, a2, a3, a4]:
            # for b in bags:
            new_bags = ef(a, bags, hard_extract=True)
            for b in new_bags:
                for r in b.regions:
                    assert r.mask.shape == (1, 1)
            # s.add(new_bag)
            # check identical hashes
        # assert len(s) == 1


def test_bg(task: TaskBags):
    # typical bg == 0
    bg2 = 0
    wo_c2 = task.x[0], task.x[1], task.x[3]
    # w_c2 = task.x[2], task.x_test[0]

    p01 = Action(name=Extractors.EP, bg=bg2, c=1)
    r01 = Action(name=Extractors.ER, bg=bg2, c=1)
    p02 = Action(name=Extractors.EP, bg=bg2, c=2)
    r02 = Action(name=Extractors.ER, bg=bg2, c=2)
    efhard = partial(ef, hard_extract=True)

    # pixel regions equals primitives
    assert efhard(p01, wo_c2) == efhard(r01, wo_c2)
    assert efhard(p01, wo_c2) == efhard(p02, wo_c2)
    assert efhard(p02, wo_c2) == efhard(r02, wo_c2)
    assert efhard(r01, wo_c2) == efhard(r02, wo_c2)

    # change coords
    assert efhard(p01, wo_c2) != efhard(p01, efhard(p01, wo_c2))
    assert efhard(r01, wo_c2) != efhard(r01, efhard(r01, wo_c2))

    # no change coords
    assert efhard(p01, efhard(p01, wo_c2)) == efhard(
        p01, efhard(p01, efhard(p01, wo_c2))
    )
    assert efhard(r01, efhard(r01, wo_c2)) == efhard(
        r01, efhard(r01, efhard(r01, wo_c2))
    )
