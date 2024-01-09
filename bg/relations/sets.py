from typing import Hashable, Iterable, TypeVar

T = TypeVar("T", bound=Hashable)


def set_intersection(s1: Iterable[T], s2: Iterable[T]) -> set[T]:
    return set(s1).intersection(set(s2))
