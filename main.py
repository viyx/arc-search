import argparse
import glob
import logging
import multiprocessing as mp

import numpy as np

from datasets.arc import ARCDataset, RawTaskData
from log import config_logger
from search.start import TaskSearch


def process_task(task: RawTaskData, task_name, log_level):
    lname = config_logger(log_level, task_name)
    logger = logging.getLogger(lname)
    logger.info("Start task %s", task_name)
    ts = TaskSearch(lname, task)
    ts.init()
    ts.search_topdown()
    pred = ts.test()
    res = []
    for y, pred in zip(task.test_y, pred):
        res.append(np.all(y == pred))
    logger.info("Result for task %s: %s", task_name, res)
    return res


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--files", default="./data/arc/*/*", help="Task files")
    parser.add_argument(
        "-l",
        "--log-level",
        default="info",
        choices=["error", "debug", "info"],
        help="Logging level",
    )
    parser.add_argument(
        "-t", "--timeout", type=int, default=60, help="Timeout in seconds for each task"
    )
    parser.add_argument(
        "-p",
        "--processes",
        type=int,
        default=1,
        help="Number of parallel processes to use",
    )
    args = parser.parse_args()

    lname = config_logger(args.log_level, "main")
    logger = logging.getLogger(lname)

    tasks = glob.glob(args.files)
    ds = ARCDataset(tasks)

    # TODO timeout for single process
    if args.processes == 1:
        for i, name in enumerate(ds.task_names):
            try:
                logger.info("Running task %s without multiprocessing", name)
                res = process_task(ds[i], name, args.log_level)
                logger.info("Completed task %s with result %s", name, res)
            except RuntimeError as e:
                logger.error("Task %s encountered an error: %s", name, e)
    else:
        with mp.Pool(processes=args.processes) as pool:
            results = []
            for i, name in enumerate(ds.task_names):
                result = pool.apply_async(
                    process_task, args=(ds[i], name, args.log_level)
                )
                results.append((name, result))

            for name, result in results:
                try:
                    res = result.get(timeout=args.timeout)
                    logger.info("Completed task %s with result %s", name, res)
                except mp.TimeoutError:
                    logger.error("Task %s timed out", name)
                    continue
                except NotImplementedError as e:
                    logger.error(e, name)


if __name__ == "__main__":
    main()
