% --- Helper predicates ---

% Flatten the body into a list of atoms
flatten_body((A, B), Atoms) :- 
    flatten_body(A, AtomsA),   % Recursively flatten the left part
    flatten_body(B, AtomsB),   % Recursively flatten the right part
    append(AtomsA, AtomsB, Atoms).  % Combine the results
flatten_body(A, [A]) :- 
    A \= (_, _).  % Base case: A is a single atom, not a conjunction

% --- Condition check predicates ---

% Check if any atom in the list satisfies a given condition
check_any_cond(Condition, Head, [H|_]) :-
    \+ call(Condition, Head, H),  % If the head satisfies the condition, succeed
    !.                   % Cut to prevent further backtracking once the condition is met
check_any_cond(Condition, Head, [_|T]) :-
    check_any_cond(Condition, Head, T).  % Otherwise, check the rest of the list

% Check if all atoms in the list satisfy a given condition
check_all_cond(Condition, Head, []) :- !.  % If the list is empty, succeed
check_all_cond(Condition, Head, [H|T]) :-
    call(Condition, Head, H),  % Check if the head satisfies the condition
    check_all_cond(Condition, Head, T).  % Recursively check the rest of the list

% --- Main prune predicate ---


prune((Head :- Body)) :-
    flatten_body(Body, Atoms),  % Flatten the body into a list of atoms
    check_all_cond(check_inp, Head, Atoms),  % Succeeds if all atoms satisfy the io/2 condition
    !.

% Main prune predicate that uses both check_any_cond and check_all_cond
prune((Head :- Body)) :-
    flatten_body(Body, Atoms),  % Flatten the body into a list of atoms
    check_any_cond(check_io, Head, Atoms).  % Succeeds if any atom is an inp/4 predicate


check_inp(_Head, BodyElement):-
    \+ functor(BodyElement,inp,_).

check_io(Head, BodyElement):-
    ((functor(BodyElement,inp,IA), arg(IA,BodyElement,I2))
    -> 
        functor(Head,_,OA),
        arg(OA,Head,I1),
        I1==I2
    ;
    true
    ).