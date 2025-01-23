## Current status

- background knowledge is not full
- no metrics on full dataset, it is tested on picked up exapmles to prove a concept

## Motivation

This repository implements a prototype for solving the [ARC-AGI challenge](https://arcprize.org/arc) with **Indictive Logic Programming (ILP)** methods [[ilp introduction]](https://arxiv.org/abs/2008.07912)[[wiki]](https://en.wikipedia.org/wiki/Inductive_logic_programming). The aim of **ILP** is to produce *logic rules* which describe a given data. For example, for a [task](https://neoneye.github.io/arc/edit.html?dataset=ARC&task=f45f5ca7) on Figure 1 learned rules can be:

```prolog
output('green',X,Y) :-                                  % if there is a green input with X and Y=D+4
   input('green',X,D), plus1func(D,E), plus3func(E,Y).  % then there is a green ouptput with the X and updated Y
output('blue',X,Y) :-
   input('blue',X,D), plus1func(D,Y).
output('yellow',X,Y) :-
   input('yellow',X,D), plus3func(D,Y).
output('red',X,Y) :-
   input('red',X,D), plus2func(D,Y).
```
<em>Listing 1.</em>

However, before we start induction algorithm we need to convert raw data to objects(input and output in *Listing 1*) and we don't know how to treat the raw data in advance, for example in the task (Figure 1) we can extract ***lines*** from inputs but not ***separate pixels***, so induction would search a theory which describes how to convert lines to pixels that is highly undesirable. So we need some variablity in representations at hand.

<div style="text-align: center;">
<img src="./misc/images/move_pixels.png" alt="drawing" width="800" height="400"/>
<p><em>Figure 1. Task "Move pixels right". </em></p></div>
<em>* Images of tasks are taken from site <a href="https://neoneye.github.io/arc/" style="font-size: 13px">https://neoneye.github.io/arc</a></em>

<!-- and draw inspiration from non-monotonic reasoning [[1]](https://en.wikipedia.org/wiki/Non-monotonic_logic)[[2]](https://plato.stanford.edu/entries/logic-nonmonotonic/) -->
So we have following desiredata:
- develope top-down/bottom-up operators which extract appropriate objects iteratevly deepening/expanding
- eveluate these representation with heuristics to choose the most promising
- when representation was chosen, we can do fast induction/search of a theory/program
- use only relevant background knowledge according to representations
- 


<!-- ### Motivational example -->

<!-- 
The answer for the task in natural language is "move blocks right according to rules: red by 3, yellow by 4, green by 5, blue by 2". To find this answer in formal language we need to extract only representations as 'pixels' from input and outputs, however we don't know this in advance as we can interpret figures in outputs as lines or other more complex figures. This problem of multiple representations is *ubiqitious in `arc` dataset.  -->

Let's consider another [task](https://neoneye.github.io/arc/edit.html?dataset=ARC&task=00d62c1b) (Figure 2) which gives more intuition

<div style="text-align: center;">
<img src="./misc/images/fill_complex.png" alt="drawing" width="800" height="400"/>
<p><em>Figure 2. Task "Fill yellow". </em></p></div>

The answers for this task in words could be:
 - "Fill holes of green figures with yellow color"
 - "Recolor all rectangular black figures to yellow"


Here we already don't need 'pixel' representation as in the previous task. For the first answer we need only green complex figures and check whether they have holes, for the second task we need only black figures. Even though it is possible to imagine answer in 'pixel' representation it would have redundacy relations which makes search space for induction much more bigger(i.e "If a pixel is part of rectangular black fugure then recolor the pixel to green").

## Algorithm

The core algorithm focuses on extracting multiple representations of inputs and outputs in top-down fashion to facilitate program induction. It ranks these representations by calculating distances between inputs and outputs and use the most promising for induction attempt. For the induction process, it leverages written on `prolog` [Aleph](https://www.cs.ox.ac.uk/activities/programinduction/Aleph/aleph.html) system alongside primitive `python` solvers capable of identifying one-to-one and constant relations. Planned enhancements include the integration of new induction systems and Neiro-symbolic methods.


**Key features**:
- Generate diverse representations and evaluate them by distances.
- Utilize the most relevant background knowledge for each induction attempt.(TODO)
- Bidirectional A*-like search between representattions.
- Avoid unnecessary and redundant representations.
- Modularity. Can be extended with different distances, representation operators, induction systems.



## Basic usage:
```bash
# single file
python main.py -f ./data/arc/evaluation/f45f5ca7.json -l debug
```

```bash
# all files from two directories
python main.py -d ./data/arc/evaluation/ ./data/arc/training/
```

```bash
# run 8 processes
python main.py -p 8 -d ./data/arc/evaluation/
```

**TODO:**
- collect metrics on full datasets
- create reasonable distance
- add background knowledge ranking
- add classifications to induction(??)
- add configurations for the pipeline and a standard(like sklearn) interface for it
- add bottom-up and other extractors, list representations
- replace `python` validations with induction constraints when possible
- research table/1 predicate for data access(see [example](https://github.com/friguzzi/aleph/blob/master/prolog/examples/weather.pl))
- introduce nueur-symbolic methods