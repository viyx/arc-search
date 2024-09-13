from typing import Any, Hashable

from reprs.primitives import TaskBag
from search.answer import Answer

ALEPH_START = """
:- use_module(aleph).
:- aleph.
:- style_check(-discontiguous).
:- aleph_set(evalfn,posonly).
:- aleph_set(check_redundant,true).
:- aleph_set(clauselength,4).
:- aleph_set(clauses,3).
"""

ALEPH_END = """
flatten_body((A, B), Atoms) :-
    flatten_body(A, AtomsA),   % Recursively flatten the left part
    flatten_body(B, AtomsB),   % Recursively flatten the right part
    append(AtomsA, AtomsB, Atoms).  % Combine the results
flatten_body(A, [A]) :-
    A \\= (_, _).  % Base case: A is a single atom, not a conjunction

% Helper predicate to check if any element in a list does not satisfy cond/1
check_any_not_cond(Head, [H|_]) :-
    \\+ check_io(Head, H),  % If the head does not satisfy the condition, succeed
    !.           % Cut to prevent backtracking once a non-satisfying condition is found
check_any_not_cond(Head,[_|T]) :-
    check_any_not_cond(Head, T).  % Otherwise, check the rest of the list

prune((Head :- Body)) :-
    flatten_body(Body, Atoms),  % Flatten the body into a list of atoms
    check_any_not_cond(Head,Atoms).

prune((Head :- Body)) :-
    flatten_body(Body, Atoms),  % Flatten the body into a list of atoms
    length(Atoms, L),
    L < 1.

check_io(Head, BodyElement):-
    ((functor(BodyElement,inp,IA), arg(IA,BodyElement,I2))
    ->
        current_predicate(outp/OA),
        arg(OA,Head,I1),
        I1==I2
    ;
    true
    ).
"""


class LabelEncoder:
    def __init__(self):
        self._state = 0
        self._mapper = {}

    def __getitem__(self, value: Hashable):
        if not isinstance(value, Hashable):
            raise ValueError()
        if value in self._mapper:
            return self._mapper[value]
        self._state += 1
        self._mapper[value] = f"'{self._state}'"
        return self._mapper[value]


class Aleph:
    def __init__(self, task: TaskBag, sofar: Answer):
        self.task = task
        self.sofar = sofar
        self.encoder = LabelEncoder()

    def _generate_facts(self, name: str, facts: list[Any]) -> str:
        return "\n".join(f"{name}({f})." for f in facts)

    def _bg_pos(self) -> str:
        inps = []
        outps = []
        all_mh = set()
        all_ch = set()
        for i, b in enumerate(self.task.x.bbags, 1):
            for r in b.regions:
                all_mh.add(self.encoder[r.mask_hash])
                all_ch.add(self.encoder[r.color_hash])
                inps.append(
                    f"""inp({r.x},{r.y},{r.width},{r.height},{self.encoder[r.mask_hash]},
                    {self.encoder[r.color_hash]},{i})."""
                )
        inps = "\n".join(inps)
        for i, b in enumerate(self.task.y.bbags, 1):
            for r in b.regions:
                terms = []
                for f in self.sofar.need_fields:
                    if f == "mask_hash":
                        t = self.encoder[getattr(r, f)]
                        all_mh.add(t)
                    elif f == "color_hash":
                        t = self.encoder[getattr(r, f)]
                        all_ch.add(t)
                    else:
                        t = str(getattr(r, f))
                    terms.append(t)
                outps.append(f"outp({','.join(terms)},{i}).")

        bg = f"""
:-begin_bg.

btw(A,B,C):-
    integer(A),
    integer(B),
    between(A, B, C).

plus1(A,B):-
    integer(A),
    B is A + 1.

minus1(A,B):-
    integer(A),
    B is A - 1.

{self._generate_facts("ii",
                      range(1, len(self.task.x.bbags)+len(self.task.x_test.bbags)+1))}

{self._generate_facts("nn", range(1, 31))}

{self._generate_facts("mask", all_mh)}

{self._generate_facts("color", all_ch)}

{inps}
:-end_bg."""
        pos = "\n:-begin_in_pos.\n" + "\n".join(outps) + "\n:-end_in_pos."
        return bg + pos

    def _modes_dets(self) -> str:
        types_maps = {
            "x": "nn",
            "y": "nn",
            "width": "nn",
            "height": "nn",
            "mask_hash": "mask",
            "color_hash": "color",
        }
        str_fields = ["mask_hash", "color_hash"]

        outp_modes = []
        for f in self.sofar.need_fields:
            if f in str_fields:
                outp_modes.append(f"#{types_maps[f]}")
            else:
                outp_modes.append(f"+{types_maps[f]}")

        mh = f""":- modeh({len(self.sofar.need_fields)+1}
        ,outp({','.join(outp_modes)},+ii))."""
        others_modes = f"""
:- modeb(*,inp(-nn,+nn,+nn,+nn,#mask,#color,-ii)).
:- modeb(*,inp(+nn,-nn,+nn,+nn,#mask,#color,-ii)).
:- modeb(*,inp(-nn,-nn,+nn,+nn,#mask,#color,-ii)).
:- modeb(*,btw(+nn,+nn,+nn)).
:- modeb(*,btw(+nn,+nn,-nn)).
:- modeb(*,plus1(+nn,+nn)).
:- modeb(*,plus1(+nn,-nn)).
:- modeb(*,minus1(+nn,+nn)).
:- modeb(*,minus1(+nn,-nn)).
:- determination(outp/{len(outp_modes)+1},inp/7).
:- determination(outp/{len(outp_modes)+1},btw/3).
:- determination(outp/{len(outp_modes)+1},plus1/3).
:- determination(outp/{len(outp_modes)+1},minus1/3).
        """
        return mh + others_modes

    def write_file(self) -> None:
        s = ALEPH_START + self._modes_dets() + self._bg_pos() + ALEPH_END
        with open("prolog/aleph/aleph_test.pl", "w") as al:
            al.write(s)
