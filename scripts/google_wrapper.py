import json
import logging
from pathlib import Path

import typer
from typing_extensions import Annotated

from scripts.google_search_api import GoogleSearchAPI


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

    with open(input_path, 'r', encoding='utf-8') as f:
        logging.debug("Reading data from %s", input_path)
        data = json.load(f)

    
    google = GoogleSearchAPI()
    
    for company in data:
        if (company["url"] == "" or company["url"] == None) and (company["name"] != "" or company["name"] != None):
            logging.debug("Searching on Google for %s", company["name"])
            company["url"] = google.search(company["name"])
    
    with open(Path(output_path), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        logging.info("Data written to %s", output_path)
    
if __name__ == "__main__":
    typer.run(main)