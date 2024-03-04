"""
This module contains a wrapper function for extracting text from raw HTML in the scraped data and inserting it into the mongo database.
"""
import json
import logging
from datetime import datetime
from enum import StrEnum
from pathlib import Path

import tldextract
import typer
from mongo import get_client
from pymongo.errors import WriteError
from typing_extensions import Annotated

from definitions import ROOT_DIR
from scripts.extract import DataExtractor
from scripts.scb import SCBinterface


class Schema(StrEnum):
    """
    Used to loosely enforce a schema for MongoDB.
        Defines database name and collection names. 
    """
    # Database
    DB              = "SCB"
    # Collections
    SCRAPED_DATA    = "scraped_data"
    EXTRACTED_DATA  = "extracted_data"
    METHODS         = "methods"

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
    mongo_client = get_client()
    mongo_client[Schema.DB][Schema.SCRAPED_DATA].create_index('company_id')
    mongo_client[Schema.DB][Schema.SCRAPED_DATA].create_index('timestamp')
    mongo_client[Schema.DB][Schema.EXTRACTED_DATA].create_index('scraped_id')
    
    interface = SCBinterface()
    extractor = DataExtractor()
    scraped_data = _open_json(input_path)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    method = [extract_meta,extract_body,p_only]

    for scraped_item in scraped_data:
        extractor.create_soup_from_string(scraped_item['raw_html'])
        extracted_text = extractor.extract(p_only=p_only, extract_body=extract_body, extract_meta=extract_meta)
        insert_extracted_data(extracted_text, scraped_item["url"], timestamp, method, interface, mongo_client)
        logging.info("Added extracted data from %s", scraped_item["url"])


def insert_extracted_data(extracted_data, url, timestamp, method, interface, client):
    """
    Inserts the extracted data into the mongo database.
    
    :param scraped_id (ObjectId): The ID of the scraped data.
    :param extracted_data (str): The extracted data.
    :param url (str): The URL of the extracted data.
    """
    url_components = tldextract.extract(url)
    # Try to find the company using the full domain subdomain.domain.tld
    company = interface.get_company_by_url(url_components.fqdn)

    # If not found, try using the base domain domain.tld
    if company is None:
        base_domain = f"{url_components.domain}.{url_components.suffix}"
        company = interface.get_company_by_url(base_domain)

    if company is None:
        logging.error("No company found for URL: %s", url)
        return None
    
    client[Schema.DB][Schema.EXTRACTED_DATA].update_one(
            {
                'company_id':company['_id'],
                'date':timestamp
            },   
            {
                "$push": 
                {
                    f"data" : {'url':url,'method':method,'data':extracted_data}
                }
            } 
        ,
        upsert=True)


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