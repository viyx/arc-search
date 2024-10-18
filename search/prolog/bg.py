from enum import Enum

from pydantic import BaseModel

NAT_TYPE = "nat"
STR_TYPE = "str"


class Types(str, Enum):
    NAT = NAT_TYPE
    STR = STR_TYPE


class Directions(str, Enum):
    IN = "+"
    OUT = "-"
    INOUT = "?"


class Argument(BaseModel):
    type: Types
    direction: Directions


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
    integer(A),
    integer(B),
    A < B."""

BASE_BG = [PLUS1FUNC, MINUS1FUNC, LESS]

BASE_BG_ARGS: dict[str, Predicate] = {
    PLUS1FUNC: Predicate(
        name="plus1func",
        args=[
            Argument(type=Types.NAT, direction=Directions.IN),
            Argument(type=Types.NAT, direction=Directions.OUT),
        ],
    ),
    MINUS1FUNC: Predicate(
        name="minus1func",
        args=[
            Argument(type=Types.NAT, direction=Directions.IN),
            Argument(type=Types.NAT, direction=Directions.OUT),
        ],
    ),
    LESS: Predicate(
        name="less",
        args=[
            Argument(type=Types.NAT, direction=Directions.IN),
            Argument(type=Types.NAT, direction=Directions.IN),
        ],
    ),
}


# def extract_functor(clause: str) -> tuple[str, list[Argument]]:
#     sig = clause.split(":-")[0]
#     i1, i2 = sig.index("("), sig.index(")")
#     pred = sig[:i1]
#     args = sig[i1 + 1 : i2].split(",")
#     res = []
#     for arg in args:
#         d = arg[0]
#         _, t = arg[1:].split("_")
#         res.append(Argument(type=t, direction=d))
#     return pred, res
