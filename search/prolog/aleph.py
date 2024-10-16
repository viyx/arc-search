from itertools import product

from search import lgg
from search.prolog.bg import NAT_TYPE, extract_functor

Ttod = list[list[dict]]

ALEPH_START = """:- use_module(aleph).
:- aleph.
:- [aleph_ext].
:- style_check(-discontiguous).
:- aleph_set(check_redundant,true).
:- aleph_set(clauselength,6).
"""


EXAMPLE_ID_TYPE = "ei"
INP_PRED = "inp"
OUT_PRED = "outp"


def make_mode(pred: str, h_or_b: str, types: list[str], n: int | None = None) -> str:
    _n = str(n) if n is not None else "*"
    return f":- mode{h_or_b}({_n},{pred}({','.join(types)}))."


def gen_facts(data: Ttod, pred: str, order: list[str], exclude: list[str]) -> list[str]:
    res = []
    for i, example in enumerate(data, 1):
        for o in example:
            values = iter(o[k] for k in order if k not in exclude)
            value_wquote = iter(
                f"'{v}'" if isinstance(v, str) else str(v) for v in values
            )
            res.append(f"{pred}({','.join(value_wquote)},{i}).")
    return res


class Aleph:
    def __init__(self, bg: list[str]):
        self._outp_args: list[str] = []
        self._inp_args: list[str] = []
        self._inp_lgg = None
        self._outp_lgg = None
        self.bg: list[str] = bg
        self.deters: list[str] = []
        self.modes: list[str] = []
        self.inp_facts: list[str] = []
        self.outp_facts: list[str] = []
        self.prolog_prog: str = ""

    @property
    def outp_consts(self) -> dict:
        return {k: v for k, v in self._outp_lgg.items() if v != lgg.VAR}

    @property
    def inp_consts(self) -> dict:
        return {k: v for k, v in self._inp_lgg.items() if v != lgg.VAR}

    @classmethod
    def _map_types(
        cls, d: dict, args: list[str], int_dirs: list[str], other_dirs: list[str]
    ) -> tuple[list[str], list[str]]:
        res_types = []
        res_dirs = []
        for k in args:
            if isinstance(d[k], int):
                res_types.append(f"{NAT_TYPE}")
                res_dirs.append(int_dirs)
            else:
                res_types.append(f"{k}")
                res_dirs.append(other_dirs)
        return res_types, res_dirs

    @classmethod
    def _gen_directions(
        cls, types: list[str], dirs: list[list[str]]
    ) -> list[list[str]]:
        prod = product(*dirs)
        res = []
        for p in prod:
            _res = []
            for d, t in zip(p, types):
                _res.append(f"{d}{t}")
            res.append(_res)
        return res

    def _add_deter(self, pred: str, arity: int) -> None:
        self.deters.append(
            f":- determination({OUT_PRED}/{len(self._outp_args) + 1},{pred}/{arity})."
        )

    def _modes_head(self, outp_sample: dict) -> None:
        types, dirs = self._map_types(outp_sample, self._outp_args, ["+"], ["#"])
        out_types = self._gen_directions(types, dirs)[0]
        self.modes.append(make_mode(OUT_PRED, "h", out_types + [f"+{EXAMPLE_ID_TYPE}"]))

    def _modes_bg(self) -> None:
        for c in self.bg:
            pred, args = extract_functor(c)
            types = [arg.direction + arg.type for arg in args]
            self.modes.append(make_mode(pred, "b", types))
            self._add_deter(pred, len(args))

    def _modes_inp(self, inp_sample: dict) -> None:
        types, dirs = self._map_types(inp_sample, self._inp_args, ["+", "-"], ["#"])
        types_wdirs = self._gen_directions(types, dirs)
        for t in types_wdirs:
            self.modes.append(make_mode(INP_PRED, "b", t + [f"-{EXAMPLE_ID_TYPE}"]))
        self._add_deter(INP_PRED, len(self._inp_args) + 1)

    def _fix_args(self, inputs: Ttod, outputs: Ttod) -> None:
        self._inp_args = list(inputs[0][0].keys() - self.inp_consts.keys())
        self._outp_args = list(outputs[0][0].keys() - self.outp_consts.keys())

    def _find_consts(self, inputs: Ttod, outputs: Ttod) -> None:
        self._inp_lgg = lgg.lgg_dict(list(lgg.lgg_dict(e) for e in inputs))
        self._outp_lgg = lgg.lgg_dict(list(lgg.lgg_dict(e) for e in outputs))

    def write_file(self, inputs: Ttod, outputs: Ttod) -> None:
        self._find_consts(inputs, outputs)
        self._fix_args(inputs, outputs)
        self._modes_head(outputs[0][0])
        self._modes_bg()
        self._modes_inp(inputs[0][0])
        self.inp_facts = gen_facts(inputs, INP_PRED, self._inp_args, self.inp_consts)
        self.outp_facts = gen_facts(
            outputs, OUT_PRED, self._outp_args, self.outp_consts
        )
        nl = "\n"
        self.prolog_prog = f"""{ALEPH_START}
% input_args:{self._inp_args}
% oupt_args:{self._outp_args}
{nl.join(self.modes)}
{nl.join(self.deters)}
{nl}:-begin_bg.
{nl.join(self.bg)}
{nl.join(self.inp_facts)}
:-end_bg.
{nl}:-begin_in_pos.
{nl.join(self.outp_facts)}
:-end_in_pos.
"""
        with open("prolog/aleph/aleph_test.pl", "w") as al:
            al.write(self.prolog_prog)
