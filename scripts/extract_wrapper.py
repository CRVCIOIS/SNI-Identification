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
                file_okay=False, 
                dir_okay=True, 
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
            extractor.create_soup_from_string(scraped_item['raw_html'])
            extracted_text = extractor.extract(p_only=p_only, extract_body=extract_body, extract_meta=extract_meta)
            insert_extracted_data(extracted_text, scraped_item["url"], scraped_item['org_nr'], timestamp, method, interface, mongo_client)
            logging.info("Added extracted data from %s", scraped_item["url"])


def insert_extracted_data(extracted_data, url, org_nr, timestamp, method, interface, client):
    """
    Inserts the extracted data into the mongo database.
    
    :param scraped_id (ObjectId): The ID of the scraped data.
    :param extracted_data (str): The extracted data.
    :param url (str): The URL of the extracted data.
    """
    
    company = interface.fetch_company_by_org_nr(org_nr)
    
    if company is None:
        return
    
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

if __name__ == '__main__':
    log_path = Path(ROOT_DIR) / "logs"
    log_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%dT%H%M%S')
    file_name = f"{Path(__file__).stem}_{timestamp}.log"
    logging.basicConfig(
                    filename=Path(log_path, file_name),
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
    typer.run(extract_wrapper)
    logging.info("Extraction finished!")
