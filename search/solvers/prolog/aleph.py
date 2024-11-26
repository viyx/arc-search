import os
import re
import subprocess
import tempfile
import threading
from ast import literal_eval
from collections import defaultdict
from collections.abc import Sequence
from datetime import datetime
from itertools import product

from search.solvers.base import Solver
from search.solvers.metafeatures import TaskMetaFeatures
from search.solvers.prolog.bg import BASE_BG_ARGS, Argument, Directions, Types
from search.solvers.prolog.negative import compose_fact, gen_neg_facts

LLD = list[list[dict]]
SSD = Sequence[Sequence[dict]]

ALEPH_START = """:- use_module('../../aleph').
:- aleph.
:- ['../../aleph_prune'].
:- style_check(-discontiguous).
:- aleph_set(check_redundant,true).
:- aleph_set(check_useless,true).
:- aleph_set(samplesize,4).
:- aleph_set(clauselength,5).
:- aleph_set(minpos,2).
:- aleph_set(verbosity,0).
"""

# TODO Create specific Transformer for Aleph input. Add #eid to the ends of regions.
# TODO Cancel answers with constant predicates outp(...) since they indicate failure.


# Change these consts carefully, they are used in aleph_prune.pl
INP_PRED = "inp"
OUT_PRED = "outp"


def make_mode(pred: str, h_or_b: str, args: list[str], n: int | None = None) -> str:
    _n = str(n) if n is not None else "*"
    return f":- mode{h_or_b}({_n},{pred}({','.join(args)}))."


def gen_facts(
    data: LLD, pred: str, args: list[str], *, startfrom: int = 1
) -> list[str]:
    res = []
    for i, example in enumerate(data, startfrom):
        for reg in example:
            vals = list(map(reg.get, args))
            res.append(compose_fact(pred, vals, i))
    return res


def extract_accuracy(data: str) -> float | None:
    accuracy = re.search(r"Accuracy\s*=\s*(\d+\.?\d*)", data)
    if accuracy:
        return float(accuracy.group(1))
    return None


def extract_max_rule(data: str) -> int | None:
    rule_ids = re.findall(r"\[Rule (\d+)\]", data)
    if len(rule_ids) > 0:
        max_rule_id = max(map(int, rule_ids))
        return max_rule_id
    return None


class AlephSWI(Solver):
    def __init__(
        self,
        parent_logger: str,
        tf: TaskMetaFeatures,
        *,
        bg: list[str],
        opt_neg_n: int,
        timeout: int,
    ):
        super().__init__(parent_logger, tf)
        self.bg = bg
        self.opt_neg_n = opt_neg_n
        self._outp_args: list[Argument] = []
        self._outp_attrs: list[str] = []
        self._inp_args: list[Argument] = []
        self._inp_attrs: list[str] = []
        self.inp_facts: list[str] = []
        self.test_facts: list[str] = []
        self.deters: list[str] = []
        self.modes: list[str] = []
        self.pos: list[str] = []
        self.neg: list[str] = []
        self.prolog_prog: str = ""
        self.timeout = timeout

        t = datetime.now().strftime("%H_%M_%S_%f")
        dname = f"./prolog/aleph/temp/{t}_{self.opt_neg_n}/"
        if not os.path.exists(dname):
            os.makedirs(dname)

        self._dir_name = dname
        self._train_file = dname + "train.pl"
        self._rules_file = dname + "rules.pl"

    def _args2aleph_types(self, args: list[Argument]) -> list[list[str]]:
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
            f":- determination({OUT_PRED}/{len(self._outp_args)},{pred}/{arity})."
        )

    def _modes_head(self, sample: dict) -> None:
        self._outp_attrs = sorted(sample.keys())
        self._outp_args = self._map_types2args(
            sample, self._outp_attrs, {"int": Directions.IN, "str": Directions.CONST}
        )
        self._outp_args.append(Argument(type=Types.EID, direction=Directions.IN))
        args_aleph = self._args2aleph_types(self._outp_args)[0]
        self.modes.append(make_mode(OUT_PRED, "h", args_aleph))

    def _modes_bg(self) -> None:
        for c in self.bg:
            pred = BASE_BG_ARGS[c]
            for arg_list in self._args2aleph_types(pred.args):
                self.modes.append(make_mode(pred.name, "b", arg_list, 2))
            self._add_deter(pred.name, len(pred.args))

    def _modes_inp(self, sample: dict) -> None:
        self._inp_attrs = sorted(sample.keys())
        self._inp_args = self._map_types2args(
            sample, self._inp_attrs, {"int": Directions.INOUT, "str": Directions.CONST}
        )
        self._inp_args.append(Argument(type=Types.EID, direction=Directions.OUT))
        args = self._args2aleph_types(self._inp_args)
        for arg_list in args:
            self.modes.append(make_mode(INP_PRED, "b", arg_list))
        self._add_deter(INP_PRED, len(self._inp_args))

    def _map_types2args(
        self, sample: dict, keys: set[str], type2dir: dict
    ) -> list[Argument]:
        _res = []
        for k in keys:
            t = sample[k].__class__.__name__
            d = type2dir[t]
            _res.append(Argument(type=Types(t), direction=d))
        return _res

    def _gen_data(self, inputs: LLD, outputs: LLD) -> None:
        self._modes_head(outputs[0][0])
        self._modes_bg()
        self._modes_inp(inputs[0][0])
        self.inp_facts = gen_facts(inputs, INP_PRED, self._inp_attrs)
        self.pos = gen_facts(outputs, OUT_PRED, self._outp_attrs)
        self.neg = gen_neg_facts(
            outputs, OUT_PRED, self._outp_attrs, self.pos, optional_n=self.opt_neg_n
        )

    def compose_train(self, inputs: LLD, outputs: LLD) -> None:
        self._gen_data(inputs, outputs)
        nl = "\n"
        dnl = nl + nl
        self.prolog_prog = f"""{ALEPH_START}
% input args order:{self._inp_attrs}
% oupt args order:{self._outp_attrs}
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

    def solve(self, x: SSD, y: SSD) -> bool:
        self.logger.debug(
            "solve with `timeout`(=%s) and `opt_neg_n`(=%s)",
            self.timeout,
            self.opt_neg_n,
        )
        self.compose_train(x, y)
        with open(self._train_file, "w", encoding="ascii") as f:
            f.write(self.prolog_prog)

        train_cmd = f"induce,aleph:write_rules('{self._rules_file}','aleph'),halt"
        self.logger.debug("train")
        stdout1, stderr1 = self._run_swipl(
            self._train_file, train_cmd, timeout=self.timeout
        )
        if stderr1 or not stdout1:
            return False
        acc = extract_accuracy(stdout1)
        max_rule = extract_max_rule(stdout1)
        if acc != 1 or max_rule >= len(self.pos):
            self.logger.info(
                "failure due to non-perfect `accuracy`(=%s) or number of `rules`(=%s)",
                acc,
                max_rule,
            )
            return False

        # simple running for checking errors and singletons
        self.logger.debug("error checking")
        _, stderr2 = self._run_swipl(self._rules_file, "halt", timeout=1)
        if stderr2:
            self.logger.error(stderr2)
            return False

        self.success = True
        return True

    def predict(self, x) -> SSD:
        if not self.success:
            raise RuntimeError("The solver has no solution.")

        start = self.tf.len_x() + 1
        self.test_facts = gen_facts(x, INP_PRED, self._inp_attrs, startfrom=start)

        with open(self._rules_file, "r", encoding="ascii") as frules:
            rules = frules.readlines()

        with tempfile.NamedTemporaryFile(
            "w", delete=False, suffix=".pl", dir=self._dir_name
        ) as tfile:
            tfile.writelines(rules)
            tfile.write("\n".join(self.bg) + "\n")
            tfile.write("\n".join(self.test_facts) + "\n")
            _vars = [chr(x) for x in range(ord("A"), ord("A") + len(self._outp_args))]
            _vars = ",".join(_vars)
            tfile.write(
                f":-setof(({_vars}),({OUT_PRED}({_vars}),{_vars[-1]}>={start}),L1),"
                + "print(L1)."
            )

        self.logger.debug("predict")
        stdout, stderr = self._run_swipl(tfile.name, "halt", timeout=1)
        if not stderr and stdout:
            test_ans: list[tuple] = literal_eval(stdout)
            res = defaultdict(list)
            for t in test_ans:
                eid = t[-1]
                _d = {}
                for i, k in enumerate(self._outp_attrs):
                    _d[k] = t[i]
                res[eid].append(_d)
            finalres = [res[k] for k in sorted(res.keys())]
            self.logger.debug("final res %s", str(finalres))
            return finalres
        return []

    def _run_swipl(
        self, fname: str, goal: str, *, timeout: int
    ) -> tuple[str | None, str | None]:
        process = None
        stdout_lines = []
        stderr_lines = []

        try:
            args = ["swipl", "-q", "-D", "encoding=utf8", "-f", fname, "-g", goal]
            process = subprocess.Popen(
                args,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.logger.debug("start swipl, args: %s", args)

            def read_stdout():
                for stdout_line in iter(process.stdout.readline, ""):
                    self.logger.debug("stdout: %s", stdout_line.strip())
                    stdout_lines.append(stdout_line)

            def read_stderr():
                for stderr_line in iter(process.stderr.readline, ""):
                    self.logger.error("stderr: %s", stderr_line.strip())
                    stderr_lines.append(stderr_line)

            stdout_thread = threading.Thread(target=read_stdout)
            stderr_thread = threading.Thread(target=read_stderr)
            stdout_thread.start()
            stderr_thread.start()

            process.wait(timeout=timeout)

            stdout_thread.join()
            stderr_thread.join()

            self.logger.debug("finish swipl, args: %s", args)

            stdout = "".join(stdout_lines) if stdout_lines else None
            stderr = "".join(stderr_lines) if stderr_lines else None

            return stdout, stderr
        except subprocess.TimeoutExpired as e:
            self.logger.error("process timed out: %s", e)
            process.kill()
            return None, None
        finally:
            if process and process.poll() is None:
                process.kill()
