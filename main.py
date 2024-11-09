import argparse
import glob
import logging
import os
from time import strftime

import numpy as np

from datasets.arc import ARCDataset
from search.start import TaskSearch

APP_LOGGER = "app"


def _init_logging(level: str) -> None:
    _logger = logging.getLogger(APP_LOGGER)
    _logger.setLevel(level.upper())
    console_handler = logging.StreamHandler()
    console_handler.setLevel("DEBUG")
    fname = strftime("./logs/%m_%d_%Y/app_%H_%M_%S.log")
    if not os.path.exists(os.path.dirname(fname)):
        os.makedirs(os.path.dirname(fname))
    file_handler = logging.FileHandler(fname, mode="a", encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s.%(msecs)03d - %(levelname)s: %(name)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)
    _logger.addHandler(console_handler)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--files", default="./data/arc/*/*")
    parser.add_argument(
        "-l", "--log", default="info", choices=["error", "debug", "info"]
    )
    args = parser.parse_args()

    _init_logging(args.log)
    tasks = glob.glob(args.files)
    ds = ARCDataset(tasks)
    logger = logging.getLogger(APP_LOGGER)
    for i, name in enumerate(tasks):
        logger.info("start task %s", name)
        ts = TaskSearch(ds[i])
        ts.search_topdown()
        res = ts.test()
        for y, pred in zip(ds[i].test_y, res):
            print("result", np.all(y == pred))
    pass
