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
from reprs.primitives import NO_BG, Bag, BGs, Region


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
        # We need order for readablility purposes.
        # There is no functional meaning here.
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


def filter_actions_by_bg(actions: set[Action], bg: int) -> set[Action]:
    return set(a for a in actions if a.bg == bg)


@lru_cache
def _all_actions() -> set[Action]:
    a = set()
    for e in Extractors:
        for b in BGs:
            for c in CONNECTIVITY:
                a.add(Action(name=e, bg=b, c=c))
    return a


# these actions do nothing but put a full copy of input into one region
INIT_ACTIONS = [
    Action(name=Extractors.ER, bg=NO_BG, c=FOUR_CONN),
    Action(name=Extractors.ER, bg=NO_BG, c=EIGHT_CONN),
]


def next_actions(
    bags: tuple[Bag], prev_actions: list[Action], *, determinate: bool
) -> set[Action]:
    "Find possible actions. Prohibit voiding(remove all content) actions."
    det_acts = _all_actions()
    # a temporary restriction
    # don't allow to apply second bg as it is irreversible operation and
    # we won't be able to reconstruct order in which bgs were applied
    if determinate and any(a.bg != NO_BG for a in prev_actions):
        det_acts = filter_actions_by_bg(det_acts, NO_BG)

    acts = set()
    voids = set()
    for b in bags:
        for r in b.regions:
            acts.update(next_actions_r(r))
            voids.update(void_color(r))
    acts = {a for a in acts if a.bg not in voids}
    return acts & det_acts


def void_color(r: Region) -> set[int]:
    "Return color if it is the only for region."
    if r.is_one_colored:
        return {r.unq_colors[0]}
    return set()


@lru_cache
def next_actions_r(r: Region) -> set[Action]:
    "Return useful actions which can be applied to region's content."
    to_pixel = Action(name=Extractors.ER, bg=NO_BG, c=NO_CONN)
    if r.is_one_colored:
        return {to_pixel}
        # add Action(name=Extractors.EP, bg=-1, c=1)??
        # give bugs if -1 is not supported in Region.raw_data
        # potentially split 8conn-primitive to a few 4conn-primitives;
        # temporary excluded as the action should already be in
        # graph, as 4,8conn are always added together, see below

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
def extract_forall(
    action: Action, bags: tuple[Bag], *, hard_extract: bool = False
) -> tuple[Bag]:
    """Apply the actions for each region in a bag.
    Skip applying if the action is not possible."""
    new_bags = []
    for b in bags:
        _bags = []
        for r in b.regions:
            if not hard_extract and action not in next_actions_r(r):
                # miss action
                rbag = Bag(regions=[r])
            else:
                rbag = action(data=r.raw_view)
            _bags.append(rbag)
        bag = Bag.merge(_bags)
        new_bags.append(bag)
    return tuple(new_bags)
