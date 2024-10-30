import enum
from functools import lru_cache, partial
from typing import Any

from pydantic import BaseModel

from reprs.extractors import (
    CONNECTIVITY,
    EIGHT_CONN,
    FOUR_CONN,
    NO_CONN,
    extract_prims,
    extract_regions,
)
from reprs.primitives import BG, NO_BG, Bag, Region


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

    def __lt__(self, other: "Action") -> bool:
        if self.name != other.name:
            return self.name < other.name
        if self.bg != other.bg:
            return self.bg < other.bg
        if self.c != other.c:
            return self.c < other.c
        return False

    def __call__(self, *args: Any, **kw: Any) -> Bag:
        return partial(self.emap()[self.name], c=self.c, bg=self.bg)(*args, **kw)

    def __repr__(self) -> str:
        #  Shorten and ajust representations to the form: `R( 1, 0)`
        i = self.name.index("_")
        firstletter = self.name[i + 1]
        bg = " " + str(self.bg) if self.bg != NO_BG else str(self.bg)
        c = " " + str(self.c) if self.c != NO_CONN else str(self.c)
        return f"{firstletter.capitalize()}({bg},{c})"

    def __str__(self) -> str:
        return self.__repr__()

    def __hash__(self) -> int:
        return hash(str([self.name, self.bg, self.c]))


def filter_nobg_actions(actions: set[Action]) -> set[Action]:
    return set(a for a in actions if is_nobg_action(a))


def is_nobg_action(action: Action) -> bool:
    return action.bg == NO_BG


@lru_cache
def _all_actions() -> set[Action]:
    a = set()
    for e in Extractors:
        for b in BG:
            for c in CONNECTIVITY:
                a.add(Action(name=e, bg=b, c=c))
    return a


INIT_ACTIONS = [
    Action(name=Extractors.ER, bg=NO_BG, c=FOUR_CONN),
    Action(name=Extractors.ER, bg=NO_BG, c=EIGHT_CONN),
]


def next_actions(
    bags: tuple[Bag], prev_actions: list[Action], determinate: bool
) -> set[Action]:
    acts = _all_actions()
    if determinate and any(a.bg != NO_BG for a in prev_actions):
        acts = filter_nobg_actions(acts)

    res = set()
    for b in bags:
        for r in b.regions:
            res.update(next_actions_r(r, determinate))
    return res & acts


@lru_cache
def next_actions_r(r: Region, remove_parts: bool) -> set[Action]:
    to_pixel = Action(name=Extractors.ER, bg=NO_BG, c=NO_CONN)
    to_void = Action(name=Extractors.ER, bg=r.unq_colors[0], c=FOUR_CONN)
    for_one_colored = set()
    if r.mask.shape == (1, 1):  # pixel
        for_one_colored = {to_void}
    elif r.is_primitive:  # not pixel
        for_one_colored = {to_pixel, to_void}
    elif r.is_one_colored:  # not primitive
        for_one_colored = {to_pixel, to_void}
        # add Action(name=Extractors.EP, bg=-1, c=1)??
        # give bugs if -1 is not supported in Region.raw_data
        # potentially split 8conn-primitive to a few 4conn-primitives;
        # temporary excluded as the action should already be in
        # graph, as 4,8conn are always added together
    if for_one_colored:
        return for_one_colored - {to_void} if remove_parts else for_one_colored
    for_many_colored = set()
    for color in r.unq_colors:
        for conn in CONNECTIVITY:
            for_many_colored.add(Action(name=Extractors.EP, bg=color, c=conn))
            b = extract_regions(r.raw_view, bg=color, c=conn)
            if len(b.regions) == 1 and b.regions[0].is_rect:
                # still the same region
                continue
            for_many_colored.add(Action(name=Extractors.ER, bg=color, c=conn))
    for_many_colored.add(to_pixel)
    for_many_colored.discard(set(INIT_ACTIONS))
    return for_many_colored


@lru_cache
def extract_flat(action: Action, bags: tuple[Bag]) -> tuple[Bag]:
    "Extract bag for each region and merge."
    new_bags = []
    for b in bags:
        _bags = []
        for r in b.regions:
            if action not in next_actions_r(r, False):
                rbag = Bag(regions=[r])
            else:
                rbag = action(data=r.raw_view)
            _bags.append(rbag)
        bag = Bag.merge(_bags)
        new_bags.append(bag)
    return tuple(new_bags)
