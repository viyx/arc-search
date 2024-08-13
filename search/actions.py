import enum
from functools import lru_cache, partial
from itertools import product
from typing import Any

from pydantic import BaseModel

from reprs.extractors import extract_prims, extract_regions
from reprs.primitives import Bag, BBag

BG = {0, -1}
CONNECTIVITY = {1, 2, -1}


class Extractors(str, enum.Enum):
    EP = "extract_prims"
    ER = "extract_regions"


class ExtractAction(BaseModel):
    name: Extractors
    bg: int
    c: int

    def _ex_maps(self) -> dict:
        return {Extractors.EP: extract_prims, Extractors.ER: extract_regions}

    def __call__(self, *args: Any, **kwds: Any) -> Bag:
        return partial(self._ex_maps()[self.name], c=self.c, bg=self.bg)(*args, **kwds)

    def __repr__(self) -> str:
        #  Example: Convert `extract_regions,1,0` -> `er(1, 0)`
        i = self.name.index("_")
        firstletters = self.name[0] + self.name[i + 1]
        return f"{firstletters}{self.c, self.bg}"

    def __str__(self) -> str:
        return self.__repr__()

    def __hash__(self) -> int:
        return hash(str([self.name, self.bg, self.c]))


def possible_actions(bbag: BBag) -> set[ExtractAction]:
    p_actions = set()
    # colors = set(c for b in bbag.bags for c in b.unq_colors)
    # all_primitive = all(b.all_primitive for b in bbag.bags)
    for b, c in product(BG, CONNECTIVITY):
        # if b == -1:  # no
        # if all_primitive:
        # continue
        # else:
        # if b not in colors:  # useless background
        # continue
        p_actions.add(ExtractAction(name=Extractors.ER, c=c, bg=b))
        p_actions.add(ExtractAction(name=Extractors.EP, c=c, bg=b))
    return p_actions


@lru_cache
def extract_flat(action: ExtractAction, bbag: BBag) -> list[Bag]:
    "Extract bag for each region -> flatten -> merge -> return."
    new_bags = []
    for b in bbag.bags:
        _bags = []
        for r in b.regions:
            rbags = action(data=r.raw_view)
            _bags.append(rbags)
        bag = Bag.merge(_bags)
        new_bags.append(bag)
    return new_bags
