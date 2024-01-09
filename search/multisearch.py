from bg.representations.convert import convert_key
from bg.representations.negative_mining import color_injury
from bg.representations.partition import partition
from datasets.arc import RawTaskData


class TaskSearch:
    def __init__(self, task: RawTaskData) -> None:
        self.task = task
        self.success = False

    def search(self):
        max_cnt = 20
        ds = []
        for i, (x, y) in enumerate(zip(self.task.train_x, self.task.train_y)):
            px = partition(x, 1)
            py = partition(y, 1)
            pos = convert_key(px, py, i * (max_cnt + 1), True)
            ds.append(pos)
            negatives = color_injury(py, max_cnt)
            for ni, sample in enumerate(negatives):
                neg = convert_key(px, sample, i * (max_cnt + 1) + ni + 1, False)
                ds.append(neg)

        npos = len(list(filter(lambda x: "pos" in x, ds)))
        nneg = len(list(filter(lambda x: "neg" in x, ds)))
        ds.insert(0, f"% summary: npos = {npos}, nneg = {nneg}")

        with open("arc_new.kb", "+w") as f:
            f.write("\n\n".join(ds) + "\n")

        # s = SearchClassification(self.task, 1, 1)
        # s.search()
