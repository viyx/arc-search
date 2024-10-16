import numpy as np
import pytest

from reprs.primitives import Region


@pytest.fixture(name="raw1")
def region_raw_data1() -> np.ndarray:
    return np.array([[0, 0, 1], [0, 1, 0], [1, 0, 0]], dtype="int8")


@pytest.fixture(name="mask_full")
def region_mask_data1(raw1: np.ndarray) -> np.ndarray:
    return np.full_like(raw1, 1, dtype=bool)


@pytest.fixture(name="mask1")
def region_mask_data2(raw1: np.ndarray) -> np.ndarray:
    return raw1 == 1


@pytest.fixture(name="mask_not1")
def region_mask_data3(raw1: np.ndarray) -> np.ndarray:
    return raw1 != 1


def test_region(raw1: np.ndarray, mask1: np.ndarray):
    r1 = Region(x=1, y=2, raw=raw1, mask=mask1)
    r2 = Region(x=2, y=2, raw=raw1, mask=mask1)

    assert r1.color_hash != r1.mask_hash != hash(r1)
    assert r1.color_hash == r2.color_hash
    assert r1.mask_hash == r2.mask_hash
    assert hash(r1) != hash(r2)
