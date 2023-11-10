import argparse
import glob

import numpy as np

from datasets.arc import ARCDataset
from search.starter import TaskSearch

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--files", default="./data/arc/*/*")
    args = parser.parse_args()

    tasks = glob.glob(args.files)
    ds = ARCDataset(tasks)
    fails = 0
    succ = 0

    for i, name in enumerate(tasks):
        # try:
        ts = TaskSearch(ds[i])
        ts.search_topdown()
        results = ts.test()
        if results is not None:
            for y, pred in zip(ds[i].test_y, results):
                s = np.all(y == pred)
                succ += s
                # print("result", np.all(y == pred))
        # except NotImplementedError:
        #     fails += 1
        # except BaseException:
        #     fails += 1
    print(succ, fails)
