"""
This module contains a wrapper function for extracting text from raw HTML in the scraped data and inserting it into the mongo database.
"""
import json
import logging
import os
from datetime import datetime
from enum import StrEnum
from pathlib import Path
import os

import tldextract
import typer
from pymongo.errors import WriteError

from typing_extensions import Annotated
from definitions import ROOT_DIR
from scripts.mongo import get_client, Schema
from scripts.extract import DataExtractor
from scripts.scb import SCBinterface

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

    logging.debug("Initializing extractor")
    
    mongo_client = get_client()
    mongo_client[Schema.DB][Schema.SCRAPED_DATA].create_index('company_id')
    mongo_client[Schema.DB][Schema.SCRAPED_DATA].create_index('timestamp')
    mongo_client[Schema.DB][Schema.EXTRACTED_DATA].create_index('scraped_id')
    logging.debug("Mongo initialized")
    interface = SCBinterface()
    logging.debug("SCB initialized")
    extractor = DataExtractor()
    logging.debug("Data extractor initialized")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    method = [extract_meta,extract_body,p_only]

    logging.debug("Extractor initialized")

    for filename in os.listdir(input_path):
        logging.debug("Extracting data from file at %s", filename)
        with open(os.path.join(input_path,filename), 'r', encoding='utf-8') as f:
                scraped_item = json.load(f)
                if('example.com' in scraped_item['domain']):
                    logging.debug("Found example.com, skipping")
                    continue
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
    
    # Spacy has a limit of 1000000 characters, so we truncate the data if it exceeds this limit
    if len(extracted_data) >= 1000000:
        logging.debug("Extracted data for company %s exceeds 1000000 characters, truncating", company['name'])
        extracted_data = extracted_data[:1000000]
    
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


# def _open_json(file_path):
#     """
#     Opens the specified file and returns its contents as a JSON object.

#     :param file_path (Path): Path to the file.
#     :returns: The contents of the file as a JSON object, 
#         or None if the file cannot be opened or is not a valid JSON file.
#     """
#     try:
#         with open(Path(file_path), 'r', encoding='utf-8') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         logging.error("File not found: %s", file_path)
#     except json.JSONDecodeError:
#         logging.error("File is not a valid JSON file: %s", file_path)
#     return None

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    typer.run(extract_wrapper)
