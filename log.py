import logging
import os
from time import strftime

APP_LOGGER = "app"


def config_logger(level: str, name: str) -> str:
    logger_name = f"{APP_LOGGER}.{name}"
    logger = logging.getLogger(logger_name)
    logger.setLevel(level.upper())

    console_handler = logging.StreamHandler()
    day, secs = strftime("%m_%d_%Y"), strftime("%H_%M_%S")
    fname = f"./logs/{day}/app_{name}_{secs}.log"

    if not os.path.exists(os.path.dirname(fname)):
        os.makedirs(os.path.dirname(fname))

    file_handler = logging.FileHandler(fname, mode="a", encoding="utf-8")
    file_formatter = logging.Formatter(
        "[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    blue_color = "\033[34m"  # Blue color for brackets
    reset_color = "\033[0m"  # Reset to default color
    console_formatter = logging.Formatter(
        f"{blue_color}[%(asctime)s.%(msecs)03d] "
        f"[%(levelname)s] "
        f"[%(name)s]{reset_color} %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    return logger_name


class AppLogger:
    def __init__(self, parent_logger: str) -> None:
        self.parent_logger = parent_logger
        self.logger = logging.getLogger(f"{parent_logger}.{self.__class__.__name__}")
