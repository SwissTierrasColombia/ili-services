import logging
from sys import stdout
from .general_config import (DEFAULT_LOG_MODE,
                             DEFAULT_LOG_FORMAT)


def setup_logging():
    pass
    # Define logger
    logger = logging.getLogger()

    # set logger level
    logger.setLevel(DEFAULT_LOG_MODE)
    logFormatter = logging.Formatter(DEFAULT_LOG_FORMAT)

    consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
    consoleHandler.setFormatter(logFormatter)
    logger.addHandler(consoleHandler)
    # logger.propagate = False