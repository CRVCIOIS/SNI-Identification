"""
This module contains a wrapper function for extracting text from raw HTML in the scraped data and inserting it into the mongo database.
"""
import json
import logging
from pathlib import Path
from scripts.extract import DataExtractor
import typer
import tldextract
from typing_extensions import Annotated
from scripts.scb import SCBinterface
from datetime import datetime


def extract_wrapper(    
            input_path: Annotated[Path, typer.Argument(
                exists=True, 
                file_okay=True, 
                dir_okay=False, 
                readable=True, 
                resolve_path=True, 
                formats=["json"], 
                help="The path to the input scraped data file."
                )],     
            extract_meta: Annotated[bool, typer.Argument()],
            extract_body: Annotated[bool, typer.Argument()],
            p_only: Annotated[bool, typer.Argument()]):
    """
    Wrapper for the extract class. Extracts text from raw HTML in the scraped data
    and inserts it into the mongodb.

    :param input_path (Path): Path to the scraped data input file.
    :param extract_meta (bool): If true, extracts meta.
    :param extract_body (bool): If true, extracts body.
    :param p_only (bool): If true, extracts only paragraphs from body.
    """
    interface = SCBinterface()
    extractor = DataExtractor()
    scraped_data = _open_json(input_path)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    methods = [extract_meta,extract_body,p_only]

    for scraped_item in scraped_data:
        """
        Extracts the domain from the URL in the form: domain.suffix, 
        for identifying the company.
        """
        domain = tldextract.extract(scraped_item["url"]).fqdn
        interface.add_scraped_data_by_url(domain, scraped_item["url"], scraped_item['raw_html'], timestamp)
        logging.info("Added scraped data from %s", scraped_item["url"])
        
        extractor.create_soup_from_string(scraped_item['raw_html'])
        extracted_text = extractor.extract(p_only=p_only, extract_body=extract_body, extract_meta=extract_meta)
        interface.add_extracted_data_by_url(domain, scraped_item["url"], extracted_text, methods, timestamp)
        logging.info("Added extracted data from %s", scraped_item["url"])


def _open_json(file_path):
    """
    Opens the specified file and returns its contents as a JSON object.

    :param file_path (Path): Path to the file.
    :returns: The contents of the file as a JSON object, 
        or None if the file cannot be opened or is not a valid JSON file.
    """
    try:
        with open(Path(file_path), 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("File not found: %s", file_path)
    except json.JSONDecodeError:
        logging.error("File is not a valid JSON file: %s", file_path)
    return None


if __name__ == '__main__':
    typer.run(extract_wrapper)