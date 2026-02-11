__all__ = ["log"]


import logging

from sys import stderr

from loguru import logger

from shared.settings import SETTINGS


def prepare_logger():
    format = (
        "<level>[{level}]</level>"
        "<g>:[{time}]</g>"
        "<m>:[{file}]</m>"
        "<m>:[{function}]</m>"
        "<m>:[{line}]</m>"
        "<w>:[{process}]</w>"
        "<w>:[{thread}]</w>"
        "<level>:[{message}]</level>"
        "<w>:[{extra}]</w>"
    )

    logger.add(
        stderr,
        level=SETTINGS.LOG_LEVEL,
        colorize=True,
        # serialize=True,
        diagnose=False,
        format=format,
        enqueue=True,
    )

    return logger


log = prepare_logger()

# peewee_logger = logging.getLogger('peewee')
# peewee_logger.addHandler(logging.StreamHandler())
# peewee_logger.setLevel(logging.DEBUG)
