import logging
from settings import Settings
from datetime import datetime
import os
from logging import Logger


def create_logger() -> logging.Logger:
    level: int = logging.DEBUG if Settings.MODE.is_development else logging.INFO
    format = "%(asctime)s %(levelname)s: %(message)s"
    date_format = "%m-%d-%y %H:%M:%S"
    log_folder = "logs/"
    filename: str = (
        log_folder + datetime.now().strftime(format="%m-%d-%Y %H:%M:%S") + ".log"
    )
    if not os.path.exists(path=log_folder):
        os.mkdir(path=log_folder)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level=logging.INFO)
    file_handler = logging.FileHandler(filename=filename)
    logging.basicConfig(
        handlers=[file_handler, console_handler],
        level=level,
        format=format,
        datefmt=date_format,
    )
    return logging.getLogger(name=__name__)


logger: Logger = create_logger()
