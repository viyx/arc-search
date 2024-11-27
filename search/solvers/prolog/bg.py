"""Module contains `prolog` clauses which used as background knowledge.
Also there are `python` signature descriptions of those clauses
for easy creation of mode decalrations. Every `prolog` clause has to
have respective `Predicate` description."""

from enum import Enum

from pydantic import BaseModel


class Types(str, Enum):
    INT = "int"
    STR = "str"
    EID = "eid"


class Directions(str, Enum):
    IN = "+"
    OUT = "-"
    INOUT = "?"
    CONST = "#"


class Argument(BaseModel):
    type: Types
    direction: Directions

    def __str__(self) -> str:
        return f"{self.direction}{self.type}"


class Predicate(BaseModel):
    name: str
    args: list[Argument]


# Prolog representations
PLUS1FUNC = """plus1func(A,B):-
    integer(A),
    B is A + 1."""

PLUS2FUNC = """plus2func(A,B):-
    integer(A),
    B is A + 2."""

PLUS3FUNC = """plus3func(A,B):-
    integer(A),
    B is A + 3."""


MINUS1FUNC = """minus1func(A,B):-
    integer(A),
    B is A - 1."""

MINUS2FUNC = """minus2func(A,B):-
    integer(A),
    B is A - 2."""

MINUS3FUNC = """minus3func(A,B):-
    integer(A),
    B is A - 3."""

LESSFUNC = """less(A,B):-
    (integer(A), integer(B)) -> A < B;
    (integer(A) -> (A1 is A+1, between(A1,29,B));false)."""

MORE = """more(A,B):-
    integer(A),
    integer(B),
    A > B."""

BASE_BG = [
    PLUS1FUNC,
    PLUS2FUNC,
    PLUS3FUNC,
    MINUS1FUNC,
    MINUS2FUNC,
    MINUS3FUNC,
    LESSFUNC,
]


BASE_BG_ARGS: dict[str, Predicate] = {
    PLUS1FUNC: Predicate(
        name="plus1func",
        args=[
            Argument(type=Types.INT, direction=Directions.IN),
            Argument(type=Types.INT, direction=Directions.OUT),
        ],
    ),
    PLUS2FUNC: Predicate(
        name="plus2func",
        args=[
            Argument(type=Types.INT, direction=Directions.IN),
            Argument(type=Types.INT, direction=Directions.OUT),
        ],
    ),
    PLUS3FUNC: Predicate(
        name="plus3func",
        args=[
            Argument(type=Types.INT, direction=Directions.IN),
            Argument(type=Types.INT, direction=Directions.OUT),
        ],
    ),
    MINUS1FUNC: Predicate(
        name="minus1func",
        args=[
            Argument(type=Types.INT, direction=Directions.IN),
            Argument(type=Types.INT, direction=Directions.OUT),
        ],
    ),
    MINUS2FUNC: Predicate(
        name="minus2func",
        args=[
            Argument(type=Types.INT, direction=Directions.IN),
            Argument(type=Types.INT, direction=Directions.OUT),
        ],
    ),
    MINUS3FUNC: Predicate(
        name="minus3func",
        args=[
            Argument(type=Types.INT, direction=Directions.IN),
            Argument(type=Types.INT, direction=Directions.OUT),
        ],
    ),
    LESSFUNC: Predicate(
        name="less",
        args=[
            Argument(type=Types.INT, direction=Directions.IN),
            Argument(type=Types.INT, direction=Directions.INOUT),
        ],
    ),
    MORE: Predicate(
        name="more",
        args=[
            Argument(type=Types.INT, direction=Directions.IN),
            Argument(type=Types.INT, direction=Directions.IN),
        ],
    ),
}
