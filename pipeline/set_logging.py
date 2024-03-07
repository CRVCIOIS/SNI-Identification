"""
Sets Python logging level to be used in the pipeline run
"""
import sys
import logging
import typer
from datetime import datetime

def set_logging(level=logging.DEBUG, logs_folder='logs'):
    timestamp = datetime.now().strftime('%Y-%m-%dT%H%M%S')

    logFormatter = logging.Formatter('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s')
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler(
        "{0}/{1}.log".format(logs_folder, timestamp),
        mode='a',
        encoding='utf-8')
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(level)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(level)
    rootLogger.addHandler(consoleHandler)

def main(
        python_logging_level: str = typer.Argument(),
        logs_folder: str = typer.Argument()):
    
    match python_logging_level.upper():
        case "DEBUG":
            level = logging.DEBUG
        case "INFO":
            level = logging.INFO
        case "WARNING":
            level = logging.WARNING
        case "ERROR":
            level = logging.ERROR
        case "CRITICAL":
            level = logging.CRITICAL
        case _:
            level = logging.NOTSET

    set_logging(level,logs_folder)

if __name__ == "__main__":
    typer.run(main)
