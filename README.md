# Multirepresentation Induction Solver.

## Motivation

This repository implements a *prototype* to address the [ARC-AGI challenge](https://arcprize.org/arc) using *Inductive Logic Programming (ILP)* methods [[ILP Introduction]](https://arxiv.org/abs/2008.07912) [[Wiki]](https://en.wikipedia.org/wiki/Inductive_logic_programming) and ideas behind common human biases.


One of goals of ILP is to generate *logical rules* that describe data using sound procedures with garanties, even if amount of examples is small. For example, in the task "Move pixels right" shown in *Figure 1*, the following rules can be learned:

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

<p align="center"><em>Listing 1. Example of generated rules.</em></p>

However, before applying the induction algorithm, the raw data must first be converted into objects (e.g., `input` and `output` in *Listing 1*), and it is unknown how to transform data in advance for the ARC tasks. For example, in the task shown in *Figure 1*, if we apply *connectivity*, we can extract *lines* from the input instead of individual *pixels*. So, if the induction process attempts to describe how to convert lines to pixels (lines in input, pixels in output), it can fail. Thus, we require flexibility in the choice of representations.

<div align="center">
<img src="./misc/images/move_pixels.png" alt="Task 'Move pixels right'" width="800" height="400"/>
<p><em>Figure 1. Task: "Move pixels right".</em></p></div>
<em style="font-size: 10px" align="left">* Task images are sourced from <a href="https://neoneye.github.io/arc/">https://neoneye.github.io/arc</a></em>



To build further intuition, let us consider another task (*Figure 2*).

<div align="center">
<img src="./misc/images/fill_complex.png" alt="Task 'Fill yellow'" width="800" height="400"/>
<p><em>Figure 2. Task: "Fill yellow".</em></p>
</div>

The answers for this task can be expressed in natural language as:

- "Fill holes in green figures with yellow color."
- "Recolor all rectangular black figures to yellow."

In this case, the *pixel* representation from the previous task is no longer necessary. For the first answer, we only require green objects and need to check for holes. For the second answer, we only need black objects and assess rectangularness. While a pixel-level answer is possible, it introduces redundant relationships that significantly increase the induction space. For example, for pixel representation the answer could be: "If a pixel is part of a rectangular black figure, then recolor the pixel to green" and for object representation: "If a figure is rectangular, then recolor it to yellow." It is obvious that the last answer will be shorter in formal language(the task even can be translated to classification).

 Ideas described above are follows from logic behind ***human's common reasoning capabilities*** as well as assumption about ***joint distribution of representations and inductions***, namely:
  - Count of objects participating in induction process should be small
  - If the answer has seqential steps and memorization, count of steps should be small
  - Sequential programs should be easely parameterized (i.e. *extend line to right until the border*)
  - Unification of objects should be fast (due to humans visual preception)
  - Description legnth of the answer in natural language has to be shorter
  - All process of finding the answer is non-monotonic
  - Induction should be fast

and other human biases.

The most relevant papers tackling the ARC-AGI challenge with ILP are:
1. Program Synthesis using Inductive Logic Programming for the Abstraction and Reasoning Corpus. [arXiv:2405.06399](https://arxiv.org/abs/2405.06399)
   - Implements ILP techniques tailored to ARC tasks, focusing on logical rule synthesis.
   - Based on the **FOIL** induction system.
2. Relational decomposition for program synthesis. [arXiv:2408.12212](https://arxiv.org/abs/2408.12212)
   - Proposes methods for decomposing relational structures to improve program synthesis.
   - Presented here method of decomposition (*Listing 1*) is inspired by this paper.
   - Based on **Popper** induction system ([link](https://github.com/logic-and-learning-lab/Popper/)).

## Algorithm

The core algorithm focuses on sequential extracting multiple representations of inputs and outputs in a top-down fashion to facilitate program induction. Representations are ranked by calculating symbolic distances between inputs and outputs, with the most promising representations selected for futher induction. These distances may include geometric, symbolic, or informational metrics to evaluate representation suitability (e.g., RIBL, edit-distance, compression level, etc.). The induction process uses universal ILP system [Aleph](https://www.cs.ox.ac.uk/activities/programinduction/Aleph/aleph.html) written in `Prolog`, supplemented by primitive `Python` solvers capable of identifying one-to-one and constant relationships. Planned enhancements include integrating additional induction systems and neuro-symbolic methods or reinforcement learning.


**Main algorithm (roughly)**:
1. Extract representations in top-down fashion
2. Calculate distancies between input and ouputs
3. Add representations and distancies to queue
4. Choose nearest representations from queue
5. Do induction with chosen representations
6. If induction fails due to timeout or don't agree with requirements goto 1

**Induction algorithm (roughly)**:
1. Take relevant to representaions background knowledge
2. Configure language bias maximally reducing search space
3. Make negative examples
4. Start induction


## Basic Usage

### Running the Prototype

#### Single File
```bash
python main.py -f ./data/arc/evaluation/f45f5ca7.json -l debug
```

#### Multiple Files
```bash
python main.py -d ./data/arc/evaluation/ ./data/arc/training/
```

#### Parallel Execution
```bash
python main.py -p 8 -d ./data/arc/evaluation/
```

## TODO

- Collect metrics for the full dataset.
- Develop a robust distance function.
- Implement background knowledge ranking.
- Add classification as a special case of program induction.
- Introduce configurable pipelines with standardized (e.g., sklearn) interfaces.
- Add bottom-up and other extraction methods, list-like representations, input-output mutually dependent representations.
- Replace `Python` validations with induction constraints wherever possible.
- Research the `table/1` predicate for data access (see [example](https://github.com/friguzzi/aleph/blob/master/prolog/examples/weather.pl)).
- Introduce neuro-symbolic methods.

### These examples should work

```bash
python main.py -f ./data/arc/evaluation/f45f5ca7.json -l debug
python main.py -f ./data/arc/training/4258a5f9.json -l info
```