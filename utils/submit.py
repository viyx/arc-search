import json

import numpy as np


def convert_tolab42(
    taskname: str,
    output_path: str,
    predictions: list[np.ndarray],
    n_tests: int,
    n_preds: int = 1,
):
    with open(output_path) as f:
        current = json.load(f)
        print(current)
