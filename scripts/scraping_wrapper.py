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
            exists=True, 
            file_okay=True, 
            dir_okay=False, 
            readable=True, 
            resolve_path=True, 
            formats=["json"], 
            help="The path to the output data file."
            )],
        ):
        
        client = get_client()
        query = {"url": { "$regex" : "^(?!\\s*$).+" }}
        
    
        documents = client[Schema.DB][Schema.COMPANIES].find(query)

        start_urls: str = ""
        document_length = len(list(documents))
        
        for index, company in enumerate(documents):
            if index == document_length - 1:
                start_urls += f'"{company["url"]}"'
            else:
                start_urls += f'"{company["url"]}",'
            
            


        output_path = ROOT_DIR / output_path
        command = f'scrapy crawl crawlingNLP -a start_urls={start_urls} -o {output_path}:json'.split(" ")
        logging.info("Running Scrapy crawler with the following command: %s", " ".join(command))
        subprocess.check_call(command, cwd=Path('scraping'))
    
if __name__ == "__main__":
    typer.run(main)
