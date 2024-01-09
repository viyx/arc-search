from typing import Iterator

from bg.representations.partition import partition
from datasets.arc import RawTaskData

# class Tree:
#     def __init__(self, sort_keys, group_keys) -> None:
#         self.sort_keys = sort_keys
#         self.group_keys = group_keys


#     def fit(self, X, y) -> None:
#         xs = sorted(X, key=self.key_sort)
#         ys = sorted(y, key=self.key_sort)
#         for gkx, datax in groupby(xs, self.key_group):
#             for gky, datay in groupby(ys, self.key_group):
#                 datax = set(datax)
#                 datay = set(datay)
#                 if set_intersection(datay, datax) != set(): # identity relation
#                     self._find_tree(datax, datay)

#     def _find_tree(self, X, y):


class SearchClassification:
    def __init__(
        self,
        task: RawTaskData,
        x_partition: int,
        y_partition: int,
    ) -> None:
        self.task = task
        self.success = False
        self.xs = [partition(x, x_partition) for x in task.train_x]
        self.ys = [partition(x, y_partition) for x in task.train_y]

    @property
    def pairs(self) -> Iterator:
        return zip(self.xs, self.ys)

    def search(self):
        # key_sort = lambda x: (x.color, x.x, x.y)
        # key_group = lambda x: x.color

        # for x, y in self.pairs:
        #     gx = groupby(sorted(x, key=key_sort, reverse=True), key_group)
        #     gy = groupby(sorted(y, key=key_sort, reverse=True), key_group)

        #     gxs = [set(g) for _, g in gx]
        #     gys = [set(g) for _, g in gy]

        pass
