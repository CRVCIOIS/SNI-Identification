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
from scripts.mongo import get_client
from scripts.scb import Schema


def main(
        output_path: Annotated[Path, typer.Argument(
            exists=False, 
            file_okay=True, 
            dir_okay=False, 
            readable=True, 
            resolve_path=True, 
            formats=["json"], 
            help="The path to the output data file."
            )],
        item_limit: Annotated[int, typer.Argument(
            help="The maximum number of items to scrape per domain."
        )] = 1
        ):
        client = get_client()
        query = {"url": {"$regex": r"/\S"}}
        
        logging.debug("Querying the database with the following query: %s", query)
        documents = client[Schema.DB][Schema.COMPANIES].find(query)

        start_urls: str = ""
        documents = list(documents)
        document_length = len(documents)
        logging.debug("Found %s documents in the database.", document_length)
        
        for index, company in enumerate(documents):
            if index == document_length - 1:
                start_urls += f'{company["url"]}'
            else:
                start_urls += f'{company["url"]},'
            
        # Check if ouput file exists, then delete it
        file = Path(output_path).with_suffix(".json")
        if file.exists():
            file.unlink()

        output_path = Path(ROOT_DIR) / Path(output_path)
        command = f'scrapy crawl crawlingNLP -a start_urls={start_urls} -a item_limit={item_limit} -o {output_path}:json'.split(" ")
        logging.info("Running Scrapy crawler with the following command: %s", " ".join(command))
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    typer.run(main)
