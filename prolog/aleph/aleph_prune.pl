flatten_body((A, B), Atoms) :- 
    flatten_body(A, AtomsA),
    flatten_body(B, AtomsB),
    append(AtomsA, AtomsB, Atoms).
flatten_body(A, [A]) :- 
    A \= (_, _).

check_any_cond(Condition, Head, [H|_]) :-
    \+ call(Condition, Head, H),
    !.
check_any_cond(Condition, Head, [_|T]) :-
    check_any_cond(Condition, Head, T).

check_all_cond(_Condition, _Head, []) :- !.
check_all_cond(Condition, Head, [H|T]) :-
    call(Condition, Head, H),
    check_all_cond(Condition, Head, T).

prune((Head :- Body)) :-
    flatten_body(Body, Atoms),
    check_all_cond(check_inp, Head, Atoms),
    !.

prune((Head :- Body)) :-
    flatten_body(Body, Atoms),
    check_any_cond(check_io, Head, Atoms),
    !.

has_singletons((Head :- Body)) :-
    term_singletons((Head :- Body),S),
    S\=[].

aleph_false:-
    hypothesis(Head,Body,_,'aleph'),
    has_singletons((Head:-Body)).


% doesn't work, just debug
% aleph_false:-
%     hypothesis(Head,_,_,'aleph'),
%     functor(Head,_,A),
%     arg(A,Head,Id),
%     var(Id).
    % print(Id),
    % !.



check_inp(_Head, BodyElement):-
    \+ functor(BodyElement,inp,_).

check_io(Head, BodyElement):-
    ((functor(BodyElement,inp,IA), arg(IA,BodyElement,I2))
    -> 
        functor(Head,_,OA),
        arg(OA,Head,I1),
        % last arguments equals
        I1==I2
    ;
    true
    ).
