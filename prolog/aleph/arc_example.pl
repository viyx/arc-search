:- use_module(aleph).
:- aleph.
:- style_check(-discontiguous).

% :- aleph_set(evalfn,posonly).
% :- aleph_set(check_redundant,true).
% :- aleph_set(check_useless,true).
:- aleph_set(clauselength,6).
:- [aleph_ext].
% :- aleph_set(i,5).
% :- aleph_set(language,2).
% :- aleph_set(minposfrac,0.2).
% :- aleph_set(sat,reduction).
% :- aleph_set(uniform_sample,true).
% :- aleph_set(nreduce_bottom,true).
% :- aleph_set(permute_bottom,true).
% :- aleph_set(clauses,3).
% :- aleph_set(cache_clauselength,10).
% :- aleph_set(caching,true).
% :- aleph_set(search,false).
% :- aleph_set(pos_fraction,0.1).
% :- aleph_set(nodes,100000).
% :- aleph_set(samplesize,4).
% :- aleph_set(resample,4).
% :- aleph_set(permute_bottom,true).
% :- aleph_set(nreduce_bottom,true).
% :- aleph_set(search,false).




:- modeh(*,outp(+nn,+nn,#color,+ii)).
:- modeb(2,inp(+nn,-nn,#color,-ii)).
:- modeb(2,inp(-nn,+nn,#color,-ii)).
:- modeb(*,less_eq(+nn,+nn)).


:- determination(outp/4,inp/4).
:- determination(outp/4,btw/3).
% :- determination(outp/4,plus1/2).
% :- determination(outp/4,minus1/2).
:- determination(outp/4,less_eq/2).
:-begin_bg.

% btw1(A,B,C):-
%     integer(A),
%     integer(B),
%     A1 is A + 1,
%     B1 is B - 1,
%     between(A1, B1, C).

% btw(A,B,C):-
%     integer(A),
%     integer(B),
%     between(A, B, C).

less_eq(A,B):-
    integer(A),
    integer(B),
    A < B.

plus1(A,B):-
    integer(A),
    B is A + 1.

minus1(A,B):-
    integer(A),
    B is A - 1.

inp(0,3,'1',1).
inp(1,8,'1',1).
inp(4,1,'1',1).
inp(4,7,'1',1).
inp(6,1,'1',1).
inp(8,6,'1',1).
inp(9,3,'1',1).
inp(0,4,'1',2).
inp(0,9,'1',2).
inp(2,4,'1',2).
inp(2,8,'1',2).
inp(3,2,'1',2).
inp(7,0,'1',2).
inp(7,7,'1',2).
inp(9,6,'1',2).
inp(0,6,'1',3).
inp(0,11,'1',3).
inp(2,10,'1',3).
inp(4,5,'1',3).
inp(5,1,'1',3).
inp(5,9,'1',3).
inp(6,6,'1',3).
inp(6,10,'1',3).
inp(7,2,'1',3).
inp(9,4,'1',3).
inp(9,8,'1',3).
inp(11,4,'1',3).
inp(11,8,'1',3).
inp(0,1,'1',4).
inp(0,4,'1',4).
inp(2,4,'1',4).
inp(2,6,'1',4).
inp(3,0,'1',4).
inp(4,5,'1',4).
inp(5,2,'1',4).
inp(5,7,'1',4).
inp(7,0,'1',4).
:-end_bg.

:-begin_in_pos.
outp(0,3,'1',1).
outp(1,3,'8',1).
outp(1,8,'1',1).
outp(2,3,'8',1).
outp(3,3,'8',1).
outp(4,1,'1',1).
outp(4,2,'8',1).
outp(4,3,'8',1).
outp(4,4,'8',1).
outp(4,5,'8',1).
outp(4,6,'8',1).
outp(4,7,'1',1).
outp(5,1,'8',1).
outp(5,3,'8',1).
outp(6,1,'1',1).
outp(6,3,'8',1).
outp(7,3,'8',1).
outp(8,3,'8',1).
outp(8,6,'1',1).
outp(9,3,'1',1).
outp(0,4,'1',2).
outp(0,5,'8',2).
outp(0,6,'8',2).
outp(0,7,'8',2).
outp(0,8,'8',2).
outp(0,9,'1',2).
outp(1,4,'8',2).
outp(2,4,'1',2).
outp(2,5,'8',2).
outp(2,6,'8',2).
outp(2,7,'8',2).
outp(2,8,'1',2).
outp(3,2,'1',2).
outp(7,0,'1',2).
outp(7,1,'8',2).
outp(7,2,'8',2).
outp(7,3,'8',2).
outp(7,4,'8',2).
outp(7,5,'8',2).
outp(7,6,'8',2).
outp(7,7,'1',2).
outp(9,6,'1',2).
outp(0,6,'1',3).
outp(0,7,'8',3).
outp(0,8,'8',3).
outp(0,9,'8',3).
outp(0,10,'8',3).
outp(0,11,'1',3).
outp(1,6,'8',3).
outp(2,6,'8',3).
outp(2,10,'1',3).
outp(3,6,'8',3).
outp(3,10,'8',3).
outp(4,5,'1',3).
outp(4,6,'8',3).
outp(4,10,'8',3).
outp(5,1,'1',3).
outp(5,2,'8',3).
outp(5,3,'8',3).
outp(5,4,'8',3).
outp(5,5,'8',3).
outp(5,6,'8',3).
outp(5,7,'8',3).
outp(5,8,'8',3).
outp(5,9,'1',3).
outp(5,10,'8',3).
outp(6,6,'1',3).
outp(6,7,'8',3).
outp(6,8,'8',3).
outp(6,9,'8',3).
outp(6,10,'1',3).
outp(7,2,'1',3).
outp(9,4,'1',3).
outp(9,5,'8',3).
outp(9,6,'8',3).
outp(9,7,'8',3).
outp(9,8,'1',3).
outp(10,4,'8',3).
outp(10,8,'8',3).
outp(11,4,'1',3).
outp(11,5,'8',3).
outp(11,6,'8',3).
outp(11,7,'8',3).
outp(11,8,'1',3).
outp(0,1,'1',4).
outp(0,2,'8',4).
outp(0,3,'8',4).
outp(0,4,'1',4).
outp(1,4,'8',4).
outp(2,4,'1',4).
outp(2,5,'8',4).
outp(2,6,'1',4).
outp(3,0,'1',4).
outp(4,0,'8',4).
outp(4,5,'1',4).
outp(5,0,'8',4).
outp(5,2,'1',4).
outp(5,3,'8',4).
outp(5,4,'8',4).
outp(5,5,'8',4).
outp(5,6,'8',4).
outp(5,7,'1',4).
outp(6,0,'8',4).
outp(7,0,'1',4).
:-end_in_pos.

:-begin_in_neg.
outp(7,0,'1',5).
outp(5,6,'1',4).
outp(5,7,'8',4).
outp(6,0,'1',4).
outp(7,0,'8',4).
outp(0,3,'8',1).
outp(1,8,'8',1).
outp(4,1,'8',1).
outp(4,7,'8',1).
outp(6,1,'8',1).
outp(8,6,'8',1).
outp(9,3,'8',1).
outp(0,4,'8',2).
outp(0,9,'8',2).
outp(2,4,'8',2).
outp(2,8,'8',2).
outp(3,2,'8',2).
outp(7,0,'8',2).
outp(7,7,'8',2).
outp(9,6,'8',2).
outp(0,6,'8',3).
outp(0,11,'8',3).
outp(2,10,'8',3).
outp(4,5,'8',3).
outp(5,1,'8',3).
outp(5,9,'8',3).
outp(6,6,'8',3).
outp(6,10,'8',3).
outp(7,2,'8',3).
outp(9,4,'8',3).
outp(9,8,'8',3).
outp(11,4,'8',3).
outp(11,8,'8',3).
outp(0,1,'8',4).
outp(0,4,'8',4).
outp(2,4,'8',4).
outp(2,6,'8',4).
outp(3,0,'8',4).
outp(4,5,'8',4).
outp(5,2,'8',4).
outp(5,7,'8',4).
outp(7,0,'8',4).
outp(1,3,'1',1).
outp(2,3,'1',1).
outp(3,3,'1',1).
outp(4,2,'1',1).
outp(4,3,'1',1).
outp(4,4,'1',1).
outp(4,5,'1',1).
outp(4,6,'1',1).
outp(5,1,'1',1).
outp(5,3,'1',1).
outp(6,3,'1',1).
outp(7,3,'1',1).
outp(8,3,'1',1).
outp(0,5,'1',2).
outp(0,6,'1',2).
outp(0,7,'1',2).
outp(0,8,'1',2).
outp(1,4,'1',2).
outp(2,5,'1',2).
outp(2,6,'1',2).
outp(2,7,'1',2).
outp(7,1,'1',2).
outp(7,2,'1',2).
outp(7,3,'1',2).
outp(7,4,'1',2).
outp(7,5,'1',2).
outp(7,6,'1',2).
outp(0,7,'1',3).
outp(0,8,'1',3).
outp(0,9,'1',3).
outp(0,10,'1',3).
outp(1,6,'1',3).
outp(2,6,'1',3).
outp(3,6,'1',3).
outp(3,10,'1',3).
outp(4,6,'1',3).
outp(4,10,'1',3).
outp(5,2,'1',3).
outp(5,3,'1',3).
outp(5,4,'1',3).
outp(5,5,'1',3).
outp(5,6,'1',3).
outp(5,7,'1',3).
outp(5,8,'1',3).
outp(5,10,'1',3).
outp(6,7,'1',3).
outp(6,8,'1',3).
outp(6,9,'1',3).
outp(9,5,'1',3).
outp(9,6,'1',3).
outp(9,7,'1',3).
outp(10,4,'1',3).
outp(10,8,'1',3).
outp(11,5,'1',3).
outp(11,6,'1',3).
outp(11,7,'1',3).
outp(0,2,'1',4).
outp(0,3,'1',4).
outp(1,4,'1',4).
outp(2,5,'1',4).
outp(4,0,'1',4).
outp(5,0,'1',4).
outp(5,3,'1',4).
outp(5,4,'1',4).
outp(5,5,'1',4).
outp(5,6,'1',4).
outp(6,0,'1',4).
:-end_in_neg.


% o2(X,Y,'1',I):-inp(X,Y,'1',I).
% o2(X,Y,'8',I):-inp(X,Y1,'1',I),inp(X,Y2,'1',I),plus1(Y1,Y11),minus1(Y2,Y22),btw(Y11,Y22,Y).
% o2(X,Y,'8',I):-inp(X1,Y,'1',I),inp(X2,Y,'1',I),plus1(X1,X11),minus1(X2,X22),btw(X11,X22,X).

% o1(X,Y,'1',I):-inp(X,Y,'1',I).
% o1(X,Y,'8',I):-inp(X,Y1,'1',I),inp(X,Y2,'1',I),btw1(Y1,Y2,Y).
% o1(X,Y,'8',I):-inp(X1,Y,'1',I),inp(X2,Y,'1',I),btw1(X1,X2,X).


% flatten_body((A, B), Atoms) :- 
%     flatten_body(A, AtomsA),
%     flatten_body(B, AtomsB),
%     append(AtomsA, AtomsB, Atoms).
% flatten_body(A, [A]) :- 
%     A \= (_, _).

% check_any_cond(Condition, Head, [H|_]) :-
%     \+ call(Condition, Head, H),
%     !.
% check_any_cond(Condition, Head, [_|T]) :-
%     check_any_cond(Condition, Head, T).

% check_all_cond(_Condition, _Head, []) :- !.
% check_all_cond(Condition, Head, [H|T]) :-
%     call(Condition, Head, H),
%     check_all_cond(Condition, Head, T).

% prune((Head :- Body)) :-
%     flatten_body(Body, Atoms),
%     check_all_cond(check_inp, Head, Atoms),
%     !.

% prune((Head :- Body)) :-
%     flatten_body(Body, Atoms),
%     check_any_cond(check_io, Head, Atoms),
%     !.


% % prune((_Head :- Body)) :-
% %     flatten_body(Body, Atoms),
% %     include(is_inp, Atoms, L),
% %     length(L,Le),
% %     Le =\= 2,
% %     !.

% % is_inp(Term) :-
% %     Term =.. [inp|_].

% check_inp(_Head, BodyElement):-
%     \+ functor(BodyElement,inp,_).

% check_io(Head, BodyElement):-
%     ((functor(BodyElement,inp,IA), arg(IA,BodyElement,I2))
%     -> 
%         functor(Head,_,OA),
%         arg(OA,Head,I1),
%         I1==I2
%     ;
%     true
%     ).
    
    % TO RUN:
    % induce_max.

%     [Rule 1] [Pos cover = 37 Neg cover = 0]
% outp(A,B,'1',C) :-
%    inp(A,B,'1',C).

% [Rule 2] [Pos cover = 24 Neg cover = 0]
% outp(A,B,'8',C) :-
%    inp(D,B,'1',C), less_eq(D,A), inp(E,B,'1',C), less_eq(A,E).

% [Rule 3] [Pos cover = 45 Neg cover = 0]
% outp(A,B,'8',C) :-
%    inp(A,D,'1',C), less_eq(D,B), inp(A,E,'1',C), less_eq(B,E).