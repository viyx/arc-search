from enum import Enum

from pydantic import BaseModel

# NAT_TYPE = "nat"
# STR_TYPE = "str"
# EXAMPLE_ID_TYPE = "ei"


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


PLUS1FUNC = """plus1func(A,B):-
    integer(A),
    B is A + 1."""

MINUS1FUNC = """minus1func(A,B):-
    integer(A),
    B is A - 1."""

LESS = """less(A,B):-
    (integer(A), integer(B)) -> A < B;
    (integer(A) -> (A1 is A+1, between(A1,29,B));false)."""

MORE = """more(A,B):-
    integer(A),
    integer(B),
    A > B."""

# BASE_BG = [PLUS1FUNC, MINUS1FUNC, LESS, MORE]
CURRENT_BG = [LESS]

BASE_BG_ARGS: dict[str, Predicate] = {
    PLUS1FUNC: Predicate(
        name="plus1func",
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
    LESS: Predicate(
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
