### Decription

This repository implements a prototype for solving the ARC-AGI challenge.
The core algorithm focuses on extracting multiple representations of the same task to facilitate program induction. To evaluate these representations, it calculates the distance between input and output representations. For the induction process, it leverages the Aleph system alongside primitive solvers capable of identifying one-to-one relations and constants. Planned enhancements include the integration of new induction systems.

**Key features**:
- Generate diverse representations and evaluate them using an A*-like algorithm.
- Utilize the most relevant background knowledge for each induction attempt.(TODO)
- Implement bidirectional search to enable distinct representations for inputs and outputs.
- Avoid unnecessary and redundant representations.



### Basic usage:
```bash
# single file
python main.py -f ./data/arc/evaluation/f45f5ca7.json -l debug
```

```bash
# all files from two directories
python main.py -d ./data/arc/evaluation/ ./data/arc/training/ -l info
```

```bash
# run 8 processes
python main.py -p 8 -d ./data/arc/evaluation/
```

**TODO:**
- create reasonable metric.
- explore background knowledge ranking.
- add classifications to induction.
- add a feature to pass priority actions from terminal arguments.
- add configurations for the pipeline and a standard(sklearn) interface for it.
- replace `python` validations with induction constraints when possible.