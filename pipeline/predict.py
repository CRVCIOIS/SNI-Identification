import os
import logging
import json
import typer
import spacy
from pathlib import Path
from typing_extensions import Annotated
from classes.scraper import Scraper
from classes.extract import DataExtractor
from adapters.scb import SCBAdapter

def main(model_path: Annotated[Path, typer.Argument(..., dir_okay=True)] = "training/model-best", test_url: Annotated[str, typer.Argument()] =  ""):
    nlp = spacy.load(model_path)
    
    scraper = Scraper()
    file_name = scraper.scrape_one(test_url)
    
    with open(file_name, 'r', encoding='utf-8') as f:
        raw_html = json.load(f)['raw_html']
    
    os.unlink(file_name)
    
    extractor = DataExtractor()
    extractor.create_soup_from_string(raw_html)
    test_data = extractor.extract(extract_body=True, extract_meta=True)
    
    predictions = nlp(test_data).cats
    
    sorted_predictions = sorted(predictions.items(), key=lambda x: x[1], reverse=True)

    scb_adapter = SCBAdapter()
    codes = scb_adapter.fetch_codes()
    
    for label, score in sorted_predictions[:10]:
        logging.info(f"{label}: {codes[label]} - {score}")

    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    typer.run(main)