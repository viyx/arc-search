## Current Status

- Background knowledge is incomplete.
- Metrics on the full dataset are not available; the approach has been tested only on selected examples to demonstrate the concept.

## Motivation

This repository implements a prototype for solving the [ARC-AGI challenge](https://arcprize.org/arc) using **Inductive Logic Programming (ILP)** methods [[ILP Introduction\]](https://arxiv.org/abs/2008.07912) [[Wiki\]](https://en.wikipedia.org/wiki/Inductive_logic_programming). The goal of **ILP** is to generate *logical rules* that describe a given dataset. For example, in the [task](https://neoneye.github.io/arc/edit.html?dataset=ARC\&task=f45f5ca7) shown in Figure 1, the following rules can be learned:

```prolog
output('green', X, Y) :-                                  % If there is a green input with X and Y=D+4
   input('green', X, D), plus1func(D, E), plus3func(E, Y). % then there is a green output with X and updated Y
output('blue', X, Y) :-
   input('blue', X, D), plus1func(D, Y).
output('yellow', X, Y) :-
   input('yellow', X, D), plus3func(D, Y).
output('red', X, Y) :-
   input('red', X, D), plus2func(D, Y).
```

<p style="text-align:center;"><em>Listing 1.</em></p>

However, before applying the induction algorithm, the raw data must be converted into objects (e.g., `input` and `output` in *Listing 1*). We do not know how to treat raw data in advance. For instance, in the task from Figure 1, we can extract ***lines*** from the inputs rather than ***individual pixels***. If induction tries to describe how to convert lines to pixels, it would lead to undesirable outcomes and can fail. Thus, we require flexibility in the representations used.

<div style="text-align: center;">
<img src="./misc/images/move_pixels.png" alt="drawing" width="800" height="400"/>
<p><em>Figure 1. Task "Move pixels right". </em></p></div>
<em>* Images of tasks are taken from site <a href="https://neoneye.github.io/arc/" style="font-size: 13px">https://neoneye.github.io/arc</a></em>


### Objectives

To achieve the desired outcomes, the following steps are outlined:

- Develop top-down and bottom-up operators that iteratively extract appropriate objects.
- Evaluate these representations with heuristics to identify the most promising ones.
- Once a representation is chosen, perform fast induction and theory/program search.
- Use only relevant background knowledge based on the chosen representations.

Let us examine another [task](https://neoneye.github.io/arc/edit.html?dataset=ARC\&task=00d62c1b) (Figure 2) to gain further intuition.

<div style="text-align: center;">
<img src="./misc/images/fill_complex.png" alt="drawing" width="800" height="400"/>
<p><em>Figure 2. Task "Fill yellow". </em></p></div>

The answers for this task can be expressed in natural language as:

- "Fill holes in green figures with yellow color."
- "Recolor all rectangular black figures to yellow."

In this case, we no longer need the 'pixel' representation as in the previous task. For the first answer, we only require green complex figures and must check for holes. For the second answer, we only need black figures and check rectangularness. While a pixel-level answer is conceivable, it introduces redundant relationships that significantly increase the induction search space (e.g., for pixel representation: "If a pixel is part of a rectangular black figure, then recolor the pixel to green"; for object representation: "If a figure is rectangular, then recolor it to yellow").

## Algorithm

The core algorithm focuses on extracting multiple representations of inputs and outputs in a top-down fashion to facilitate program induction. Representations are ranked by calculating distances between inputs and outputs, with the most promising representations selected for induction. The induction process uses the [Aleph](https://www.cs.ox.ac.uk/activities/programinduction/Aleph/aleph.html) system written in `Prolog`, supplemented by primitive `Python` solvers capable of identifying one-to-one and constant relationships. Planned enhancements include integrating additional induction systems and neuro-symbolic methods.

### Key Features

- Generate diverse representations and evaluate them based on distances.
- Utilize the most relevant background knowledge for each induction attempt.
- Perform bidirectional A\*-like search between representations.
- Avoid unnecessary and redundant representations.
- Modular design, enabling the extension with different distances, representation operators, and induction systems.

## Basic Usage

```bash
# Single file
python main.py -f ./data/arc/evaluation/f45f5ca7.json -l debug
```

```bash
# All files from two directories
python main.py -d ./data/arc/evaluation/ ./data/arc/training/
```

```bash
# Run 8 processes
python main.py -p 8 -d ./data/arc/evaluation/
```

## TODO

- Collect metrics on full datasets.
- Develop a reasonable distance function.
- Implement background knowledge ranking.
- Add classification as a special case of induction (??).
- Introduce configurations for the pipeline with a standardized (e.g., sklearn-like) interface.
- Add bottom-up and other extraction methods, and list representations.
- Replace `Python` validations with induction constraints wherever possible.
- Research the `table/1` predicate for data access (see [example](https://github.com/friguzzi/aleph/blob/master/prolog/examples/weather.pl)).
- Introduce neuro-symbolic methods.