"""
Provides a consistent configuration for logging.
"""
import os
import logging.config
from datetime import datetime

LOGS_FOLDER = 'logs'
FILE_LOG_LEVEL = "DEBUG"
CONSOLE_LOG_LEVEL = "DEBUG"

def conf_logger(filename):
    """
    Applies logger configuration.

    :param filename: the file currently logging 
        (the name will be included in the log files)
    """
    logger_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s'
            },
        },
        'handlers': {
            'file': {
                'class': 'logging.FileHandler',
                'level': FILE_LOG_LEVEL,
                'formatter': 'standard',
                'filename': os.path.join(LOGS_FOLDER,'{}_{}.log'.format(
                    filename,datetime.now().strftime('%Y-%m-%dT%H%M%S'))),
                'mode': 'a',
                'encoding': 'utf-8',
            },
            'console': {
                'class': 'logging.StreamHandler',
                'level': CONSOLE_LOG_LEVEL,
                'formatter': 'standard',
                'stream': 'ext://sys.stdout',
            },
        },
        'root': {
            'handlers': ['file', 'console'],
            'level': "INFO",
        }
    }

    logging.config.dictConfig(logger_config)