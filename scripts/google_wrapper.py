"""
This module provides a wrapper function to process input data, search for company URLs on Google,
and write the updated data to an output file.
"""
import logging
from typing import Annotated

import typer

from scripts.google_search_api import GoogleSearchAPI
from scripts.scb import SCBinterface

FILTER_LIST = [
    'aktiebolag',
    'handelsbolag'
]

def _filter(original, filter_list):
    """
    Google custom search API fails to find some "too detailed" terms,
        which regular Google search succeeds.
        This function filters out these problematic terms.
    """
    name = original.lower()
    for f in filter_list:
        name = name.replace(f,'')
    return name

def main(regenerate_urls: Annotated[bool, typer.Argument()] = False):
    """
    Process the input data file, search for company URLs on Google, and update the DB.
    """

    interface = SCBinterface()
    sni_codes = interface.fetch_codes()
    
    google = GoogleSearchAPI()
    for code in sni_codes.keys():
        data = interface.fetch_companies_from_db(code, no_url=not regenerate_urls)
        for company in data:
            if 'name' in company.keys() and company["name"] != "":
                (company["url"] == "" or company["url"] is None) and 
                (company["name"] != "" or company["name"] is not None) or 
                ):
                name = _filter(company['name'], FILTER_LIST)
                logging.debug("Searching on Google for %s", name)
                company["url"] = google.search(name)
                interface.update_url_for_company(company["org_nr"], company["url"])

if __name__ == "__main__":
    #logging.basicConfig(level=logging.DEBUG)
    typer.run(main)
