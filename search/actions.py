import enum
from functools import lru_cache, partial
from itertools import product
from typing import Any

from pydantic import BaseModel

from reprs.extractors import extract_prims, extract_regions
from reprs.primitives import Bag, BBag

BG = [-1, 0]
CONNECTIVITY = [-1, 1, 2]


class Extractors(str, enum.Enum):
    EP = "extract_prims"
    ER = "extract_regions"


EMAP = {Extractors.EP: extract_prims, Extractors.ER: extract_regions}


class ExtractAction(BaseModel):
    name: Extractors
    bg: int
    c: int

    def __call__(self, *args: Any, **kwds: Any) -> Bag:
        return partial(EMAP[self.name], c=self.c, bg=self.bg)(*args, **kwds)

    def __repr__(self) -> str:
        #  Example: Format `extract_regions,1,0` -> `er(1, 0)`
        i = self.name.index("_")
        firstletters = self.name[0] + self.name[i + 1]
        return f"{firstletters}{self.c, self.bg}"

    def __str__(self) -> str:
        return self.__repr__()

    def __hash__(self) -> int:
        return hash(str([self.name, self.bg, self.c]))


def exclude_bg_actions(actions: set[ExtractAction]) -> set[ExtractAction]:
    return set(a for a in actions if a.bg == -1)


def possible_actions(bbag: BBag) -> set[ExtractAction]:
    p_actions = set()
    colors = set(c for b in bbag.bbags for c in b.unq_colors)
    all_primitive = all(b.all_primitive for b in bbag.bbags)
    all_irreducible = all(b.all_irreducible for b in bbag.bbags)
    for b, c in product(BG, CONNECTIVITY):
        # bg = -1 --> only EP
        if all_irreducible:  # need? can remove noise/unnecessary objects
            continue
        if b == -1:
            if not all_primitive or c == -1:
                p_actions.add(ExtractAction(name=Extractors.EP, c=c, bg=b))
            continue
        elif b in colors:
            p_actions.add(ExtractAction(name=Extractors.ER, c=c, bg=b))
            p_actions.add(ExtractAction(name=Extractors.EP, c=c, bg=b))
    return p_actions


@lru_cache
def extract_flat(action: ExtractAction, bbag: BBag) -> list[Bag]:
    "Extract bag for each region -> flatten -> merge -> return."
    new_bags = []
    for b in bbag.bbags:
        _bags = []
        for r in b.regions:
            rbags = action(data=r.raw_view)
            _bags.append(rbags)
        bag = Bag.merge(_bags)
        new_bags.append(bag)
    return new_bags
