import numpy as np
import pytest

from reprs.primitives import Region


@pytest.fixture(name="disconnected")
def data1() -> Region:
    data = np.array([[0, 0, 1], [1, 0, 0]])
    return Region(x=0, y=0, raw=data, mask=np.full_like(data, True, dtype=bool))


@pytest.fixture(name="connected_4")
def data2() -> Region:
    data = np.array([[0, 0, 1], [0, 0, 1], [1, 0, 0]])
    return Region(x=0, y=0, raw=data, mask=np.full_like(data, True, dtype=bool))


@pytest.fixture(name="connected_8")
def data3() -> Region:
    data = np.array([[0, 0, 1], [0, 0, 1], [0, 1, 0]])
    return Region(x=0, y=0, raw=data, mask=np.full_like(data, True, dtype=bool))


# def test_actions_redundancy(task: TaskBags,
#                             all_actions: set[ExtractAction],
#                             init_action: ExtractAction):

# for _, bags in task:
#     pa1 = possible_actions(bags)
#     assert all_actions > pa1
#     assert init_action not in pa1
