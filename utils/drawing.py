from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.axes import Axes

from datasets.arc import TaskData

CMAP = [
    "black",
    "blue",
    "red",
    "green",
    "yellow",
    "gray",
    "purple",
    "orange",
    "cyan",
    "coral",
]


def plot_array(axes: Axes, data: np.ndarray, title: str) -> None:
    cmap = colors.ListedColormap(
        [
            "#000000",
            "#0074D9",
            "#FF4136",
            "#2ECC40",
            "#FFDC00",
            "#AAAAAA",
            "#F011BE",
            "#FF851B",
            "#7FDBFF",
            "#870C25",
        ]
    )
    norm = colors.Normalize(vmin=0, vmax=9)

    axes.imshow(data, cmap=cmap, norm=norm)
    axes.grid(True, which="both", color="lightgrey", linewidth=0.5)
    axes.set_yticks([x - 0.5 for x in range(1 + len(data))])
    axes.set_xticks([x - 0.5 for x in range(1 + len(data[0]))])
    axes.set_xticklabels([])
    axes.set_yticklabels([])
    axes.set_title(title)


def plot_task(task: TaskData, predictions: np.ndarray | None = None) -> None:
    train_x, train_y, test_x, test_y = (
        task.train_x,
        task.train_y,
        task.test_x,
        task.test_y,
    )
    num_train = len(train_x)
    _, axs = plt.subplots(2, num_train, figsize=(3 * num_train, 3 * 2))
    for i in range(num_train):
        plot_array(axs[0, i], train_x[i], "train-input")
        plot_array(axs[1, i], train_y[i], "train-output")
    plt.tight_layout()
    plt.show()

    num_test = len(test_x)
    _, axs = plt.subplots(2, num_test, figsize=(3 * num_test, 3 * 2), squeeze=False)

    for i in range(num_test):
        plot_array(axs[0, i], test_x[i], "test-input")
        plot_array(axs[1, i], test_y[i], "test-output")
    plt.tight_layout()
    plt.show()

    if predictions:
        num_preds = len(predictions)
        _, axs = plt.subplots(
            2, num_preds, figsize=(3 * num_preds, 3 * 2), squeeze=False
        )

        for i in range(num_preds):
            plot_array(axs[0, i], test_x[i], "test-input")
            plot_array(axs[1, i], predictions[i], "test-prediction")
            plt.tight_layout()
            plt.show()


def plot_xy(x: np.ndarray, y: np.ndarray) -> None:
    _, axs = plt.subplots(2, 1, figsize=(3 * 1, 3 * 2))
    plot_array(axs[0], x, "input")
    plot_array(axs[1], y, "output")
    plt.tight_layout()
    plt.show()
