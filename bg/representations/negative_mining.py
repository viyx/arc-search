import itertools
from random import choice, random

from bg.representations.base_classes import Figure


def color_injury(image: set[Figure], max_count: int) -> list[set[Figure]]:
    assert isinstance(image, set)
    valid_colors = {f.color for f in image}

    full_permutations = set()
    perms = list(itertools.permutations(valid_colors))[1:]

    for perm in perms:
        mapping = dict(zip(valid_colors, perm))
        f = frozenset(f.model_copy(update={"color": mapping[f.color]}) for f in image)
        full_permutations.add(f)

    if len(full_permutations) >= max_count:
        return list(full_permutations)[:max_count]

    residual = set()
    for _ in range(max_count - len(full_permutations)):
        r = set()
        for f in image:
            if random() > 0.7:
                perm = choice(perms)
                mapping = dict(zip(valid_colors, perm))
                r.add(f.model_copy(update={"color": mapping[f.color]}))
            else:
                r.add(f)
        residual.add(frozenset(r))

    checked = (full_permutations | residual) - frozenset(image)
    return list(checked)
