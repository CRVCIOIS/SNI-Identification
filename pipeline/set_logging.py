"""
Sets Python logging level to be used in the pipeline run
"""
import logging
import typer

def main(python_logging_level: str = typer.Argument()):
    python_logging_level = python_logging_level.upper()
    match python_logging_level:
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

    logging.basicConfig(level=level)

if __name__ == "__main__":
    typer.run(main)
