from collections.abc import Sequence

from reprs.primitives import COORD_MAX, COORD_MIN, Region

SSD = Sequence[Sequence[dict]]


def validate_positions(data: SSD) -> bool:
    return _val_no_occlusion(data) and _val_proper_bounds(data)


def _val_no_occlusion(data: SSD) -> bool:
    "Checks if there are distinct regions at the same position."
    coord_keys = Region.position_props()
    for x in data:
        grid = {}
        for r in x:
            pos = frozenset((k, v) for k, v in r.items() if k in coord_keys)
            _data = set((k, v) for k, v in r.items() if k not in coord_keys)
            if pos in grid and grid[pos] != _data:
                return False
            grid[pos] = _data
    return True


def _val_proper_bounds(data: SSD) -> bool:
    "Checks positional bounds."
    coord_keys = Region.position_props()
    for x in data:
        for r in x:
            for k, v in r.items():
                if k in coord_keys and (v < COORD_MIN or v > COORD_MAX):
                    return False
    return True
