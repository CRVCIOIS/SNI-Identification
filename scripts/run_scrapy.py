import subprocess
from pathlib import Path
import typer

ROOT_DIR = Path(__file__).resolve().parents[1] 


def run_scrapy(
    start_urls: str = typer.Argument(...), 
    output_file_path: Path = typer.Argument(..., exists=False, dir_okay=False)):
    """
    Run Scrapy crawler with the given start URLs and output file path.

    :param start_urls (str): The start URLs for the Scrapy crawler, 
        NOTE: the urls must be separated by comma only i.e no space allowed.
    :param output_file_path (Path): The path to the output file.
    """

    output_file_path = ROOT_DIR / output_file_path
    command = f'scrapy crawl crawlingNLP -a start_urls={start_urls} -o {output_file_path}:json'.split(" ")
    subprocess.check_call(command, cwd=Path('scraping'))


if __name__ == '__main__':
    typer.run(run_scrapy)