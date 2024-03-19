"""
This module runs the extraction scripts on the scraped data.
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
import typer
from typing_extensions import Annotated
from classes.extract import DataExtractor
from adapters.scb import SCBAdapter
from adapters.extract import ExtractAdapter

def main(    
            scraped_data_folder: Annotated[Path, typer.Argument(
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
    Extracts text from raw HTML in the scraped data
    and inserts it into the database.

    :param input_path (Path): Path to the scraped data folder.
    :param extract_meta (bool): If true, extracts the HTML meta-tags.
    :param extract_body (bool): If true, extracts the HTML body.
    :param p_only (bool): If true, extracts only the paragraphs (<p>...</p>) from the HTML body.
    """

    scb_adapter = SCBAdapter()
    extractor = DataExtractor()
    extract_adapter = ExtractAdapter()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    methods = [extract_meta,extract_body,p_only]
    label_count = {"total_length": 0, "labels": {}}

    logging.info("Starting extraction...")
    for filename in os.listdir(scraped_data_folder):
        logging.debug("Extracting data from file at %s", filename)

        with open(os.path.join(scraped_data_folder,filename), 'r', encoding='utf-8') as f:
            scraped_item = json.load(f)

            company = scb_adapter.fetch_company_by_org_nr(scraped_item['label'])

            if company is None:
                logging.error("No company found for URL: %s", scraped_item["url"])
                continue

            extractor.create_soup_from_string(scraped_item['raw_html'])

            if extractor.soup is None:
                logging.error("Couldn't create soup from %s!", scraped_item['url'])
                logging.error("Probably not a valid HTML file")
                continue

            extracted_text = extractor.extract(
                p_only=p_only, 
                extract_body=extract_body, 
                extract_meta=extract_meta)

            # Spacy has a limit of 1000000 characters,
            # so we truncate the data if it exceeds this limit
            if len(extracted_text) >= 1000000:
                logging.debug("Extracted data for company %s exceeds 1000000 characters, truncating", company['name'])
                extracted_text = extracted_text[:1000000]

            extract_adapter.insert_extracted_data(
                extracted_text,company['url'],
                company['_id'],timestamp,methods)
            
            label_count['labels'][company['branch_codes'][0]] = label_count['labels'].get(company['branch_codes'][0], 0) + 1
            label_count['total_length'] = label_count.get('total_length', 0) + len(extracted_text)
            logging.debug("Added extracted data from %s", scraped_item["url"])

    logging.info("Extraction finished")
    logging.info("Number of URLs extracted: %s", sum(label_count['labels'].values()))
    logging.info("Number of distinct labels processed: %s", len(label_count['labels']))
    logging.info("Number of URLs per label:")
    for label in dict(sorted(label_count['labels'].items())):
        logging.info("Label %s: %s extracted URLs", label, label_count['labels'][label])
        
    logging.info("Total length of extracted data: %s", label_count['total_length'])
    logging.info("Average length of extracted data per label: %s", label_count['total_length']/len(label_count['labels']))

if __name__ == '__main__':
    from aux_functions.logger_config import conf_logger
    conf_logger(Path(__file__).stem)
    typer.run(main)
