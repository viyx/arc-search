from enum import Enum

from pydantic import BaseModel

NAT_TYPE = "nat"

PLUS1FUNC = f"""plus1func(+A_{NAT_TYPE},-B_{NAT_TYPE}):-
    integer(A),
    B is A + 1."""

MINUS1FUNC = f"""minus1func(+A_{NAT_TYPE},-B_{NAT_TYPE}):-
    integer(A),
    B is A - 1."""

LESS = f"""less(+A_{NAT_TYPE},+A_{NAT_TYPE}):-
    integer(A),
    integer(B),
    A < B."""

BASE_BG = [PLUS1FUNC, MINUS1FUNC, LESS]


class Types(str, Enum):
    NAT = NAT_TYPE
    STR = "str"


class Directions(str, Enum):
    IN = "+"
    OUT = "-"
    INOUT = "?"


class Argument(BaseModel):
    type: Types
    direction: Directions


def extract_functor(clause: str) -> tuple[str, list[Argument]]:
    sig = clause.split(":-")[0]
    i1, i2 = sig.index("("), sig.index(")")
    pred = sig[:i1]
    args = sig[i1 + 1 : i2].split(",")
    res = []
    for arg in args:
        d = arg[0]
        _, t = arg[1:].split("_")
        res.append(Argument(type=t, direction=d))
    return pred, res
