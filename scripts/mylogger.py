# coding:utf-8
'''
'''

from logging import getLogger, FileHandler, StreamHandler, Formatter, DEBUG, INFO  # noqa


def get_logger(name, file_name=None, level=INFO):
    # init
    logger = getLogger(name)
    myformat1 = '%(asctime)s - %(threadName)s - %(name)s - %(levelname)s : %(message)s'  # noqa
    myformat2 = '%(name)s - %(levelname)s : %(message)s'
    formatter = Formatter(fmt=myformat2)
    if file_name is None:
        handler = StreamHandler()
    else:
        handler = FileHandler(file_name, 'w')

    # setting of logger
    logger.setLevel(level)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def get_filename(logger):
    if type(logger.handlers[0]) is FileHandler:
        return logger.handlers[0].baseFilename
    return None
