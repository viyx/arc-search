import glob

from tqdm import tqdm

from datasets.arc import ARCDataset
from decompose.primitives import Decomposer
from discovery.linear import LinearAnalyzer

if __name__ == "__main__":
    tasks = glob.glob("./data/arc/*/*")
    ds = ARCDataset(tasks)

    results = []
    valid = []

    for i, name in tqdm(enumerate(tasks)):
        d = Decomposer(ds[i])
        d.decompose()
        try:
            has_dep, sol = LinearAnalyzer.has_obj_count_dep(d.train_x, d.train_y)
            results.append(has_dep)
            if has_dep:
                valid.append(name)
        except Exception:
            results.append(False)

    print(sum(results))
    # print(valid)
