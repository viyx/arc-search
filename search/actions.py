import enum
from functools import lru_cache, partial
from typing import Any

from pydantic import BaseModel

from reprs.extractors import extract_prims, extract_regions
from reprs.primitives import Bag, Region


class Extractors(str, enum.Enum):
    EP = "extract_prims"
    ER = "extract_regions"


class Action(BaseModel):
    name: Extractors
    bg: int
    c: int

    @classmethod
    def emap(cls) -> dict:
        return {Extractors.EP: extract_prims, Extractors.ER: extract_regions}

    def __call__(self, *args: Any, **kw: Any) -> Bag:
        return partial(self.emap()[self.name], c=self.c, bg=self.bg)(*args, **kw)

    def __repr__(self) -> str:
        #  Format `extract_regions,1,0` -> `er(1, 0)`
        i = self.name.index("_")
        firstletters = self.name[0] + self.name[i + 1]
        return f"{firstletters}{self.bg, self.c}"

    def __str__(self) -> str:
        return self.__repr__()

    def __hash__(self) -> int:
        return hash(str([self.name, self.bg, self.c]))


def exclude_nobg_actions(actions: set[Action]) -> set[Action]:
    return set(a for a in actions if a.bg == -1)


BG = [-1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
CONNECTIVITY = [-1, 1, 2]
INIT_ACTIONS = {
    Action(name=Extractors.ER, bg=-1, c=1),
    Action(name=Extractors.ER, bg=-1, c=2),
}


# def possible_actions(bags: tuple[Bag]) -> set[Action]:
#     res = set()
#     colors = set(c for b in bags for c in b.unq_colors)
#     all_one_colored = all(b.all_one_colored for b in bags)
#     all_irreducible = all(b.all_irreducible for b in bags)
#     for b, c in product(BG, CONNECTIVITY):
#         if c == -1:
#             res.add(Action(name=Extractors.EP, c=c, bg=b))
#             continue
#         # bg = -1 --> only EP
#         if all_irreducible:  # need? can remove noise/unnecessary objects
#             continue
#         if b == -1:
#             if not all_one_colored:
#                 res.add(Action(name=Extractors.EP, c=c, bg=b))
#             continue
#         if b in colors:
#             res.add(Action(name=Extractors.ER, c=c, bg=b))
#             res.add(Action(name=Extractors.EP, c=c, bg=b))
#     return res


def next_actions(bags: tuple[Bag]) -> set[Action]:
    res = set()
    for b in bags:
        for r in b.regions:
            res.update(next_actions_r(r))
    return res


@lru_cache
def next_actions_r(r: Region) -> frozenset[Action]:
    to_pixel = Action(name=Extractors.ER, bg=-1, c=-1)
    if r.mask.shape == (1, 1):  # pixel
        # to void
        return frozenset([Action(name=Extractors.ER, bg=r.unq_colors[0], c=1)])
    if r.is_primitive:  # not pixel
        # to void
        return frozenset(
            [to_pixel, Action(name=Extractors.ER, bg=r.unq_colors[0], c=1)]
        )
    if r.is_one_colored:  # not primitive
        # add Action(name=Extractors.EP, bg=-1, c=1)??
        # potentially split 8conn-primitive to a few 4conn-primitives
        # temporary excluded as effect from extraction should be in
        # graph yet, because 4,8conn are always added together
        return frozenset(
            [
                to_pixel,
                # to void
                Action(name=Extractors.ER, bg=r.unq_colors[0], c=1),
            ]
        )
    res = set()
    for color in r.unq_colors:
        for conn in CONNECTIVITY:
            res.add(Action(name=Extractors.EP, bg=color, c=conn))
            b = extract_regions(r.raw_view, bg=color, c=conn)
            if len(b.regions) == 1 and b.regions[0].is_rect:
                # still the same region
                continue
            res.add(Action(name=Extractors.ER, bg=color, c=conn))
    res.add(to_pixel)
    res -= INIT_ACTIONS
    return frozenset(res)


@lru_cache
def extract_flat(action: Action, bags: tuple[Bag], check_actions=True) -> tuple[Bag]:
    "Extract bag for each region and merge"
    new_bags = []
    for b in bags:
        _bags = []
        for r in b.regions:
            if check_actions and action not in next_actions_r(r):
                rbags = Bag(regions=[r])
            else:
                rbags = action(data=r.raw_view)
            _bags.append(rbags)
        bag = Bag.merge(_bags)
        new_bags.append(bag)
    return tuple(new_bags)
