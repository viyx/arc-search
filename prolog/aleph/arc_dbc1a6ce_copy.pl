:- use_module(aleph).
:- aleph.
:- style_check(-discontiguous).
:- aleph_set(evalfn,posonly).
:- aleph_set(check_redundant,true).
:- aleph_set(clauselength,4).
:- aleph_set(clauses,3).
% :- aleph_set(tree_type,classification).
% :- aleph_set(construct_bottom,reduction).

:- modeh(*,outp(+nn,#color,+ii)).
:- modeh(*,outp(+nn,+color,+ii)).
% :- modeh(3,outp(+color,+ii)).
% :- modeh(3,outp(-color,+ii)).
:- modeb(*,inp(-nn,+nn,#color,-ii)).
:- modeb(*,inp(+nn,-nn,#color,-ii)).
% :- modeb(*,inp(+nn,-nn,+color,-ii)).
% :- modeb(*,inp(+nn,-nn,-color,-ii)).
:- modeb(*,btw(+nn,+nn,+nn)).
:- modeb(*,plus1(+nn,+nn)).
:- modeb(*,minus1(+nn,+nn)).

:- determination(outp/3,inp/4).
:- determination(outp/3,btw/3).
:- determination(outp/3,plus1/2).
:- determination(outp/3,minus1/2).
:-begin_bg.

btw(A,B,C):-
    A1 is A + 1,
    B1 is B - 1,
    between(A1, B1, C).

plus1(A,B):-
    B is A + 1.

minus1(A,B):-
    B is A - 1.

% type definitions
color('8').
color('1').
color('3').

ii(1).
ii(2).
ii(3).
ii(4).
ii(5).

nn(0).
nn(1).
nn(2).
nn(3).
nn(4).
nn(5).
nn(6).
nn(7).
nn(8).
nn(9).
nn(10).
nn(11).
nn(12).
nn(13).
nn(14).
nn(15).
nn(16).
nn(17).

inp(0,3,'1',1).
inp(1,8,'1',1).
inp(4,1,'1',1).
inp(4,7,'1',1).
% inp(6,1,'1',1).
% inp(8,6,'1',1).
% inp(9,3,'1',1).
% inp(0,4,'1',2).
% inp(0,9,'1',2).
% inp(2,4,'1',2).
% inp(2,8,'1',2).
% inp(3,2,'1',2).
% inp(7,0,'1',2).
% inp(7,7,'1',2).
% inp(9,6,'1',2).
% inp(0,6,'1',3).
% inp(0,11,'1',3).
% inp(2,10,'1',3).
% inp(4,5,'1',3).
% inp(5,1,'1',3).
% inp(5,9,'1',3).
% inp(6,6,'1',3).
% inp(6,10,'1',3).
% inp(7,2,'1',3).
% inp(9,4,'1',3).
% inp(9,8,'1',3).
% inp(11,4,'1',3).
% inp(11,8,'1',3).
% inp(0,1,'1',4).
% inp(0,4,'1',4).
% inp(2,4,'1',4).
% inp(2,6,'1',4).
% inp(3,0,'1',4).
% inp(4,5,'1',4).
% inp(5,2,'1',4).
% inp(5,7,'1',4).
% inp(7,0,'1',4).
:-end_bg.

:-begin_in_pos.
outp(1,'1',1).
outp(1,'8',2).
outp(1,'8',2).
outp(1,'8',3).
% outp('8',4).
% outp('8',3).
% outp('1',3).
:-end_in_pos.
% outp(0,3,'1',1).
% outp(1,3,'8',1).
% outp(1,8,'1',1).
% outp(2,3,'8',1).
% outp(3,3,'8',1).
% outp(4,1,'1',1).
% outp(4,2,'8',1).
% outp(4,3,'8',1).
% outp(4,4,'8',1).
% outp(4,5,'8',1).
% outp(4,6,'8',1).
% outp(4,7,'1',1).
% outp(5,1,'8',1).
% outp(5,3,'8',1).
% outp(6,1,'1',1).
% outp(6,3,'8',1).
% outp(7,3,'8',1).
% outp(8,3,'8',1).
% outp(8,6,'1',1).
% outp(9,3,'1',1).
% outp(0,4,'1',2).
% outp(0,5,'8',2).
% outp(0,6,'8',2).
% outp(0,7,'8',2).
% outp(0,8,'8',2).
% outp(0,9,'1',2).
% outp(1,4,'8',2).
% outp(2,4,'1',2).
% outp(2,5,'8',2).
% outp(2,6,'8',2).
% outp(2,7,'8',2).
% outp(2,8,'1',2).
% outp(3,2,'1',2).
% outp(7,0,'1',2).
% outp(7,1,'8',2).
% outp(7,2,'8',2).
% outp(7,3,'8',2).
% outp(7,4,'8',2).
% outp(7,5,'8',2).
% outp(7,6,'8',2).
% outp(7,7,'1',2).
% outp(9,6,'1',2).
% outp(0,6,'1',3).
% outp(0,7,'8',3).
% outp(0,8,'8',3).
% outp(0,9,'8',3).
% outp(0,10,'8',3).
% outp(0,11,'1',3).
% outp(1,6,'8',3).
% outp(2,6,'8',3).
% outp(2,10,'1',3).
% outp(3,6,'8',3).
% outp(3,10,'8',3).
% outp(4,5,'1',3).
% outp(4,6,'8',3).
% outp(4,10,'8',3).
% outp(5,1,'1',3).
% outp(5,2,'8',3).
% outp(5,3,'8',3).
% outp(5,4,'8',3).
% outp(5,5,'8',3).
% outp(5,6,'8',3).
% outp(5,7,'8',3).
% outp(5,8,'8',3).
% outp(5,9,'1',3).
% outp(5,10,'8',3).
% outp(6,6,'1',3).
% outp(6,7,'8',3).
% outp(6,8,'8',3).
% outp(6,9,'8',3).
% outp(6,10,'1',3).
% outp(7,2,'1',3).
% outp(9,4,'1',3).
% outp(9,5,'8',3).
% outp(9,6,'8',3).
% outp(9,7,'8',3).
% outp(9,8,'1',3).
% outp(10,4,'8',3).
% outp(10,8,'8',3).
% outp(11,4,'1',3).
% outp(11,5,'8',3).
% outp(11,6,'8',3).
% outp(11,7,'8',3).
% outp(11,8,'1',3).
% outp(0,1,'1',4).
% outp(0,2,'8',4).
% outp(0,3,'8',4).
% outp(0,4,'1',4).
% outp(1,4,'8',4).
% outp(2,4,'1',4).
% outp(2,5,'8',4).
% outp(2,6,'1',4).
% outp(3,0,'1',4).
% outp(4,0,'8',4).
% outp(4,5,'1',4).
% outp(5,0,'8',4).
% outp(5,2,'1',4).
% outp(5,3,'8',4).
% outp(5,4,'8',4).
% outp(5,5,'8',4).
% outp(5,6,'8',4).
% outp(5,7,'1',4).
% outp(6,0,'8',4).
% outp(7,0,'1',4).
% :-end_in_pos.

% :-begin_in_neg.
% outp(7,0,'1',5).
% outp(5,6,'1',4).
% outp(5,7,'8',4).
% outp(6,0,'1',4).
% outp(7,0,'8',4).
% outp(0,3,'8',1).
% outp(1,8,'8',1).
% outp(4,1,'8',1).
% outp(4,7,'8',1).
% outp(6,1,'8',1).
% outp(8,6,'8',1).
% outp(9,3,'8',1).
% outp(0,4,'8',2).
% outp(0,9,'8',2).
% outp(2,4,'8',2).
% outp(2,8,'8',2).
% outp(3,2,'8',2).
% outp(7,0,'8',2).
% outp(7,7,'8',2).
% outp(9,6,'8',2).
% outp(0,6,'8',3).
% outp(0,11,'8',3).
% outp(2,10,'8',3).
% outp(4,5,'8',3).
% outp(5,1,'8',3).
% outp(5,9,'8',3).
% outp(6,6,'8',3).
% outp(6,10,'8',3).
% outp(7,2,'8',3).
% outp(9,4,'8',3).
% outp(9,8,'8',3).
% outp(11,4,'8',3).
% outp(11,8,'8',3).
% outp(0,1,'8',4).
% outp(0,4,'8',4).
% outp(2,4,'8',4).
% outp(2,6,'8',4).
% outp(3,0,'8',4).
% outp(4,5,'8',4).
% outp(5,2,'8',4).
% outp(5,7,'8',4).
% outp(7,0,'8',4).
% outp(1,3,'1',1).
% outp(2,3,'1',1).
% outp(3,3,'1',1).
% outp(4,2,'1',1).
% outp(4,3,'1',1).
% outp(4,4,'1',1).
% outp(4,5,'1',1).
% outp(4,6,'1',1).
% outp(5,1,'1',1).
% outp(5,3,'1',1).
% outp(6,3,'1',1).
% outp(7,3,'1',1).
% outp(8,3,'1',1).
% outp(0,5,'1',2).
% outp(0,6,'1',2).
% outp(0,7,'1',2).
% outp(0,8,'1',2).
% outp(1,4,'1',2).
% outp(2,5,'1',2).
% outp(2,6,'1',2).
% outp(2,7,'1',2).
% outp(7,1,'1',2).
% outp(7,2,'1',2).
% outp(7,3,'1',2).
% outp(7,4,'1',2).
% outp(7,5,'1',2).
% outp(7,6,'1',2).
% outp(0,7,'1',3).
% outp(0,8,'1',3).
% outp(0,9,'1',3).
% outp(0,10,'1',3).
% outp(1,6,'1',3).
% outp(2,6,'1',3).
% outp(3,6,'1',3).
% outp(3,10,'1',3).
% outp(4,6,'1',3).
% outp(4,10,'1',3).
% outp(5,2,'1',3).
% outp(5,3,'1',3).
% outp(5,4,'1',3).
% outp(5,5,'1',3).
% outp(5,6,'1',3).
% outp(5,7,'1',3).
% outp(5,8,'1',3).
% outp(5,10,'1',3).
% outp(6,7,'1',3).
% outp(6,8,'1',3).
% outp(6,9,'1',3).
% outp(9,5,'1',3).
% outp(9,6,'1',3).
% outp(9,7,'1',3).
% outp(10,4,'1',3).
% outp(10,8,'1',3).
% outp(11,5,'1',3).
% outp(11,6,'1',3).
% outp(11,7,'1',3).
% outp(0,2,'1',4).
% outp(0,3,'1',4).
% outp(1,4,'1',4).
% outp(2,5,'1',4).
% outp(4,0,'1',4).
% outp(5,0,'1',4).
% outp(5,3,'1',4).
% outp(5,4,'1',4).
% outp(5,5,'1',4).
% outp(5,6,'1',4).
% outp(6,0,'1',4).
% :-end_in_neg.


% o1(X,Y,'1',I):-inp(X,Y,'1',I).
% o1(X,Y,'8',I):-inp(X,Y1,'1',I),inp(X,Y2,'1',I),btw(Y1,Y2,Y).
% o1(X,Y,'8',I):-inp(X1,Y,'1',I),inp(X2,Y,'1',I),btw(X1,X2,X).


% flatten_body((A, B), Atoms) :- 
%     flatten_body(A, AtomsA),   % Recursively flatten the left part
%     flatten_body(B, AtomsB),   % Recursively flatten the right part
%     append(AtomsA, AtomsB, Atoms).  % Combine the results
% flatten_body(A, [A]) :- 
%     A \= (_, _).  % Base case: A is a single atom, not a conjunction

% % Helper predicate to check if any element in a list does not satisfy cond/1
% check_any_not_cond(Head, [H|_]) :-
%     \+ check_io(Head, H),  % If the head does not satisfy the condition, succeed
%     !.           % Cut to prevent backtracking once a non-satisfying condition is found
% check_any_not_cond(Head,[_|T]) :-
%     check_any_not_cond(Head, T).  % Otherwise, check the rest of the list

% prune((Head :- Body)) :-
%     flatten_body(Body, Atoms),  % Flatten the body into a list of atoms
%     check_any_not_cond(Head,Atoms). 

% check_io(Head, BodyElement):-
%     ((functor(BodyElement,inp,IA), arg(IA,BodyElement,I2))
%     -> 
%         current_predicate(outp/OA),
%         arg(OA,Head,I1),
%         I1==I2
%     ;
%     true
%     ).
    