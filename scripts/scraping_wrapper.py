"""This script runs a Scrapy crawler with the given start URLs and output file path.

The input data file should be a JSON file containing a list of companies with their URLs.
The script reads the input file, extracts the start URLs, and runs the Scrapy crawler.
The output data is saved in a JSON file specified by the output path.
"""
import json
import logging
import subprocess
from pathlib import Path
import typer
from typing_extensions import Annotated
from definitions import ROOT_DIR


def main(
        input_path: Annotated[Path, typer.Argument(
            exists=True, 
            file_okay=True, 
            dir_okay=False, 
            readable=True, 
            resolve_path=True, 
            formats=["json"], 
            help="The path to the input data file."
            )],
        output_path: Annotated[Path, typer.Argument(
            exists=True, 
            file_okay=True, 
            dir_okay=False, 
            readable=True, 
            resolve_path=True, 
            formats=["json"], 
            help="The path to the output data file."
            )],
        ):
        """
        Run Scrapy crawler with the given start URLs and output file path.

        :param input_path (Path): The path to the input file, which comes from google_wrapper.py.
        :param output_file_path (Path): The path to the output file.
        """
        
        with open(input_path, 'r', encoding='utf-8') as f:
            logging.debug("Reading data from %s", input_path)
            data = json.load(f)
        start_urls: str = ""
        logging.debug("Looping through the data to get the start URLs for the Scrapy crawler.")
        for index, company in enumerate(data):
            if (company["url"] != "" or company["url"] != None):
                logging.debug("Adding company url '%s' to be crawled.", company["url"])
                if index == len(data) - 1:
                    start_urls += company["url"]
                else:
                    start_urls += company["url"] + ","

        output_path = ROOT_DIR / output_path
        command = f'scrapy crawl crawlingNLP -a start_urls={start_urls} -o {output_path}:json'.split(" ")
        logging.info("Running Scrapy crawler with the following command: %s", " ".join(command))
        subprocess.check_call(command, cwd=Path('scraping'))
    
if __name__ == "__main__":
    typer.run(main)
