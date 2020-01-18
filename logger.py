import logging
import sys

logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(
    format=logging_format,
    level=logging.DEBUG,
)


def get_logger(name):
    """
    get logger
    :param name: logger name
    :return:
    """
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.ERROR)
    logger.addHandler(handler)
    return logger
