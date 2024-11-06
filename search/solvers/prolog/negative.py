import random
from itertools import product

from more_itertools import random_product

LLD = list[list[dict]]


def compose_fact(pred: str, arg_vals: list[str | int], eid: int) -> str:
    m = map(lambda x: f"'{x}'" if isinstance(x, str) else str(x), arg_vals)
    return f"{pred}({','.join(m)},{eid})."


def _swap_strings(data: LLD, pred: str, args: list[str]) -> list[str]:
    str_args = [a for a in args if isinstance(data[0][0][a], str)]
    pool = {}
    for a in str_args:
        s = {d[a] for e in data for d in e}
        if len(s) > 1:
            pool[a] = s
    if not str_args or not pool:
        return []

    res = []
    for i, example in enumerate(data, 1):
        for reg in example:
            newvalues = []
            for a in args:
                if a in pool:
                    newval = list(pool[a] - {reg[a]})
                    newvalues.append(newval)
                else:
                    newvalues.append([reg[a]])
            for nw in product(*newvalues):
                res.append(compose_fact(pred, nw, i))
    return res


def _change_integers(
    data: LLD, pred: str, args: list[str], pos: list[str], n: int
) -> list[str]:
    int_args = [a for a in args if isinstance(data[0][0][a], int)]
    if not int_args:
        return []
    rng = set(range(30))
    pools = {}
    for i, example in enumerate(data, 1):
        newregs = []
        for reg in example:
            newreg = []
            for a in args:
                if a in int_args:
                    pool = rng - {reg[a]}
                else:
                    pool = [reg[a]]
                newreg.append(pool)
            newregs.append(newreg)
        pools[i] = newregs

    maxi = 2 * n
    res = []
    i = 0
    while len(res) < n and i < maxi:
        i += 1
        eid = random.randint(1, len(data))
        reg_id = random.randint(0, len(pools[eid]) - 1)
        sample = random_product(*pools[eid][reg_id])
        if (newval := compose_fact(pred, sample, eid)) not in pos:
            res.append(newval)
    return res


def gen_neg_facts(
    data: LLD, pred: str, args: list[str], pos: list[str], *, optional_n: int = 100
) -> list[str]:
    res = _swap_strings(data, pred, args)
    if optional_n > 0:
        res2 = _change_integers(data, pred, args, pos + res, optional_n)
        res.extend(res2)  # values in res2 can duplicate res' ones
    return res
