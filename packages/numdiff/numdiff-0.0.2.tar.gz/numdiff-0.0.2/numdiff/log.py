# Authors: Benjamin Vial
# This file is part of pytmod
# License: GPLv3
# See the documentation at bvial.info/pytmod


__all__ = ["set_log_level", "logger"]


import logging

from colorlog import ColoredFormatter

LEVELS = dict(
    DEBUG=logging.DEBUG,
    INFO=logging.INFO,
    WARNING=logging.WARNING,
    ERROR=logging.ERROR,
    CRITICAL=logging.CRITICAL,
)
LOGFORMAT = (
    "  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s"
)

formatter = ColoredFormatter(LOGFORMAT)
stream = logging.StreamHandler()

stream.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.handlers = []
logger.propagate = False
logger.addHandler(stream)


def set_log_level(level):
    """Sets the log level.

    Parameters
    ----------
    level : str
        The verbosity level.
        Valid values are ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR`` or ``CRITICAL``.

    """

    LOG_LEVEL = LEVELS[level]
    logger.setLevel(LOG_LEVEL)
    stream.setLevel(LOG_LEVEL)


