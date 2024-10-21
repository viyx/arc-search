import subprocess
from itertools import product
from random import randint
from time import strftime

from search import lgg
from search.prolog.bg import BASE_BG_ARGS, Argument, Directions, Types

LLD = list[list[dict]]

ALEPH_START = """:- use_module('../aleph').
:- aleph.
:- ['../aleph_prune'].
:- style_check(-discontiguous).
:- aleph_set(check_redundant,true).
:- aleph_set(clauselength,6).
"""


EXAMPLE_ID_TYPE = "ei"
INP_PRED = "inp"
OUT_PRED = "outp"


def make_mode(pred: str, h_or_b: str, args: list[str], n: int | None = None) -> str:
    _n = str(n) if n is not None else "*"
    return f":- mode{h_or_b}({_n},{pred}({','.join(args)}))."


def gen_facts(data: LLD, pred: str, args: list[str], start: int = 1) -> list[str]:
    res = []
    for i, example in enumerate(data, start):
        for o in example:
            args_wquotes = iter(
                f"'{o[a]}'" if isinstance(o[a], str) else str(o[a]) for a in args
            )
            res.append(f"{pred}({','.join(args_wquotes)},{i}).")
    return res


def gen_neg_facts(data: LLD, pred: str, args: list[str]) -> list[str]:
    str_args = [a for a in args if isinstance(data[0][0][a], str)]
    pool = {}
    for a in str_args:
        s = {d[a] for e in data for d in e}
        assert len(s) > 1
        pool[a] = s

    res = []
    for i, example in enumerate(data, 1):
        for o in example:
            # prioritize changing strings fields and leaving integer fields unchanged
            if len(str_args) > 0:
                for sa in str_args:
                    newvalues = []
                    for a in args:
                        if a == sa:
                            # possible randomization
                            new_val = (pool[a] - {o[a]}).pop()
                            newvalues.append(f"'{new_val}'")
                        else:
                            newvalues.append(str(o[a]))
                    res.append(f"{pred}({','.join(newvalues)},{i}).")
            else:
                # change integer fields randomly
                for a in args:
                    newvalues.append(str(o[a] + randint(0, 3)))
                res.append(f"{pred}({','.join(newvalues)},{i}).")
    return res


class Aleph:
    def __init__(self, bg: list[str]):
        self.bg = bg
        self._outp_args: list[Argument] = []
        self._outp_attrs: list[str] = []
        self._inp_args: list[Argument] = []
        self._inp_attrs: list[str] = []
        self._inp_lgg = None
        self._outp_lgg = None
        self.inp_facts: list[str] = []
        self.test_facts: list[str] = []
        self.deters: list[str] = []
        self.modes: list[str] = []
        self.pos: list[str] = []
        self.neg: list[str] = []
        self.prolog_prog: str = ""

    @property
    def outp_consts(self) -> dict:
        return {k: v for k, v in self._outp_lgg.items() if v != lgg.VAR}

    @property
    def inp_consts(self) -> dict:
        return {k: v for k, v in self._inp_lgg.items() if v != lgg.VAR}

    def _map_args(self, args: list[Argument]) -> list[list[str]]:
        args_ext: list[list[Argument]] = []
        for arg in args:
            if arg.direction == Directions.INOUT:
                args_ext.append(
                    [
                        Argument(direction=Directions.IN, type=arg.type),
                        Argument(direction=Directions.OUT, type=arg.type),
                    ]
                )
            else:
                args_ext.append([arg])

        res = []
        for arg_list in product(*args_ext):
            res.append(list(map(str, arg_list)))
        return res

    def _add_deter(self, pred: str, arity: int) -> None:
        self.deters.append(
            f":- determination({OUT_PRED}/{len(self._outp_args) + 1},{pred}/{arity})."
        )

    def _modes_head(self, sample: dict) -> None:
        self._outp_attrs = sorted(sample.keys() - self.outp_consts.keys())
        self._outp_args = self._map_types2args(
            sample, self._outp_attrs, {"int": Directions.IN, "str": Directions.CONST}
        )
        args = self._map_args(self._outp_args)[0]
        self.modes.append(make_mode(OUT_PRED, "h", args + [f"+{EXAMPLE_ID_TYPE}"]))

    def _modes_bg(self) -> None:
        for c in self.bg:
            pred = BASE_BG_ARGS[c]
            for arg_list in self._map_args(pred.args):
                self.modes.append(make_mode(pred.name, "b", arg_list, 1))
            self._add_deter(pred.name, len(pred.args))

    def _modes_inp(self, sample: dict) -> None:
        self._inp_attrs = sorted(sample.keys() - self.inp_consts.keys())
        self._inp_args = self._map_types2args(
            sample, self._inp_attrs, {"int": Directions.INOUT, "str": Directions.CONST}
        )
        args = self._map_args(self._inp_args)
        if len(args) > 1:
            for arg_list in args:
                self.modes.append(
                    make_mode(INP_PRED, "b", arg_list + [f"-{EXAMPLE_ID_TYPE}"])
                )
        else:
            self.modes.append(
                make_mode(INP_PRED, "b", arg_list + [f"-{EXAMPLE_ID_TYPE}"])
            )
        self._add_deter(INP_PRED, len(self._inp_args) + 1)

    def _map_types2args(
        self, sample: dict, keys: set[str], type2dir: dict
    ) -> list[Argument]:
        _res = []
        for k in keys:
            t = sample[k].__class__.__name__
            d = type2dir[t]
            _res.append(Argument(type=Types(t), direction=d))
        return _res

    def _lggs(self, inputs: LLD, outputs: LLD) -> None:
        self._inp_lgg = lgg.lgg_dict(list(lgg.lgg_dict(e) for e in inputs))
        self._outp_lgg = lgg.lgg_dict(list(lgg.lgg_dict(e) for e in outputs))

    def _gen_data(self, inputs: LLD, outputs: LLD, test: LLD) -> None:
        self._lggs(inputs, outputs)
        self._modes_head(outputs[0][0])
        self._modes_bg()
        self._modes_inp(inputs[0][0])
        self.inp_facts = gen_facts(inputs + test, INP_PRED, self._inp_attrs)
        # self.test_facts = gen_facts(test, INP_PRED, inp_args, len(inputs)+1)
        self.pos = gen_facts(outputs, OUT_PRED, self._outp_attrs)
        self.neg = gen_neg_facts(outputs, OUT_PRED, self._outp_attrs)

    def compose_prog(self, inputs: LLD, outputs: LLD, test: LLD) -> None:
        self._gen_data(inputs, outputs, test)
        nl = "\n"
        dnl = nl + nl
        self.prolog_prog = f"""{ALEPH_START}
% input args order:{self._inp_args}
% oupt args order:{self._outp_args}
{nl.join(self.modes)}
{nl.join(self.deters)}{nl}
:-begin_bg.
{dnl.join(self.bg)}
{nl.join(self.inp_facts)}
:-end_bg.{dnl}
:-begin_in_pos.
{nl.join(self.pos)}
:-end_in_pos.{nl}
:-begin_in_neg.
{nl.join(self.neg)}
:-end_in_neg.
"""

    def run(self, inputs: LLD, outputs: LLD, test: LLD):
        self.compose_prog(inputs, outputs, test)
        try:
            dname = "./prolog/aleph/temp/"
            fname = strftime("%H_%M_%S.pl")

            with open(dname + fname, "w", encoding="utf-8") as file:
                file.write(self.prolog_prog)

            with subprocess.Popen(
                [
                    "swipl",
                    "-q",
                    "-f",
                    dname + fname,
                    "-g",
                    f"induce,aleph:write_rules('{dname}rules.pl','aleph'),halt",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            ) as process:
                stdout, stderr = process.communicate(timeout=20)

                if stderr:
                    print(f"Error: {stderr}")
                pass

        except subprocess.TimeoutExpired:
            process.kill()
            return "Prolog execution timed out."
