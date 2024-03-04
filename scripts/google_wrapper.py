"""
This module provides a wrapper function to process input data, search for company URLs on Google,
and write the updated data to an output file.
"""
import logging
from typing import Annotated
import time

import typer
from scripts.google_search_api import GoogleSearchAPI
from scripts.scb import SCBinterface

FILTER_LIST = [
    'aktiebolag',
    'handelsbolag'
]

BLACKLIST = [
    'allabolag.se',
    'facebook.com',
    'facebook.se',
    'linkedin.com',
    'kompass.com',
    'apple.com',
    'orebro.se',
    'worldsbiggestcompanies.com',
    'kreditrapporten.se',
    'utsidan.se',
    'lansstyrelsen.se',
    'barometern.se'
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

def main(regenerate_urls: Annotated[bool, typer.Argument()] = False, limit: Annotated[int, typer.Argument()] = 2):
    """
    Process the input data file, search for company URLs on Google, and update the DB.

    Args:
        regenerate_urls (bool): Flag indicating whether to regenerate URLs or not.

    Returns:
        None
    """
    interface = SCBinterface()
    sni_codes = interface.fetch_codes()
    
    totalSearches = 0
    
    google = GoogleSearchAPI()
    for code in sni_codes.keys():
        count = 0
        data = interface.fetch_companies_from_db(code, no_url=not regenerate_urls)
        for company in data:
            if count >= limit:
                break
            if 'name' in company.keys() and company["name"] != "":
                name = _filter(company['name'], FILTER_LIST)
                logging.debug("Searching on Google for %s", name)
                if totalSearches >= 100:
                    logging.warning("Reached the limit of 100 searches, waiting for 60 seconds.")
                    time.sleep(60)
                    totalSearches = 0
                company["url"] = google.search(name)
                totalSearches += 1
                count += 1
                
                if (company["url"] and not any(bl in company["url"] for bl in BLACKLIST)):
                    # If the url is found and does not contain, update the DB
                    logging.debug("Updating URL for %s to %s", company["name"], company["url"])
                    interface.update_url_for_company(company["org_nr"], company["url"])
                else:
                    logging.debug("No URL found for %s, or the url is in BLACKLIST. Deleting from DB", company["name"])
                    interface.delete_company_from_db(company["org_nr"])

if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    typer.run(main)
