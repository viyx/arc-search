import glob
import logging
import multiprocessing as mp
import os
from argparse import ArgumentParser

import numpy as np

from datasets.arc import ARCDataset, RawTaskData
from log import config_logger
from search.go import TaskSearch


def process_task(task: RawTaskData, task_name, log_level, nodes: str | None):
    log_name = config_logger(log_level, task_name)
    logger = logging.getLogger(log_name)
    logger.info("start task %s", task_name)
    ts = TaskSearch(log_name, task)
    if nodes:
        x, y = nodes.split("@")
        ts.add_priority_nodes(x, y)
    ts.search_topdown()
    pred = ts.test()
    res = []
    for y, pred in zip(task.test_y, pred):
        res.append(np.all(y == pred))
    logger.info("result for task %s: %s", task_name, res)
    return res


def parse() -> ArgumentParser:
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-f", "--file", help="Load single file.")
    group.add_argument(
        "-d", "--directories", nargs="*", help="Load files from directories."
    )
    parser.add_argument(
        "-l",
        "--log-level",
        default="info",
        choices=["error", "debug", "info"],
        help="Logging level",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=60,
        help="Timeout in seconds for each task. Works only in multiprocessing regime",
    )
    parser.add_argument(
        "-p",
        "--processes",
        type=int,
        default=1,
        help="Number of parallel processes to use",
    )
    # Example: "Reg(-1, 1) --> Prim( 0,-1)@Reg(-1, 1) --> Prim( 0,-1)".
    parser.add_argument(
        "-n",
        "--nodes",
        type=str,
        help="Manually set the highest priority to nodes.",
    )
    return parser


#  TODO. Add accuracy metric and referencies to solutions for fast access.
def main():
    args = parse().parse_args()

    lname = config_logger(args.log_level, "main")
    logger = logging.getLogger(lname)
    if args.file:
        tasks = [args.file]
    else:
        tasks = []
        for d in args.directories:
            tasks.extend(glob.glob(os.path.join(d, "*.json")))
    ds = ARCDataset(tasks)

    if args.processes == 1:
        for i, name in enumerate(ds.task_names):
            try:
                logger.info("running task %s without multiprocessing", name)
                process_task(ds[i], name, args.log_level, args.nodes)
            except RuntimeError as e:
                logger.error("task %s encountered an error: %s", name, e)
    else:
        with mp.Pool(processes=args.processes) as pool:
            results = []
            for i, name in enumerate(ds.task_names):
                # in multiprocessing regime add task name into logger name
                result = pool.apply_async(
                    process_task, args=(ds[i], name, args.log_level, args.nodes)
                )
                results.append((name, result))

            for name, result in results:
                try:
                    result.get(timeout=args.timeout)
                except mp.TimeoutError:
                    logger.error("task %s timed out", name)
                    continue
                except NotImplementedError as e:
                    logger.error(e, name)


if __name__ == "__main__":
    main()
