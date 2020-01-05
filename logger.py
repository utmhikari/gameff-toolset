import logging

logging.basicConfig(
    format='[%(name)s][%(asctime)s][%(levelname)s]: %(message)s',
)


def get_logger(name):
    """
    get logger
    :param name: logger name
    :return:
    """
    return logging.getLogger(name)
