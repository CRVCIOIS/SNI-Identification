"""
This module provides a wrapper function to process input data, search for company URLs on Google,
and write the updated data to an output file.
"""
import logging
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

def main():
    """
    Process the input data file, search for company URLs on Google, and update the DB.
    """

    interface = SCBinterface()
    sni_codes = interface.fetch_codes()
    
    google = GoogleSearchAPI()
    for code in sni_codes.keys():
        data = interface.fetch_companies_from_db(code, no_url=True)
        for company in data:
            if (company["url"] == "" or company["url"] is None) and (company["name"] != "" or company["name"] is not None):
                name = _filter(company['name'], FILTER_LIST)
                logging.debug("Searching on Google for %s", name)
                company["url"] = google.search(name)
                
                # If the url is found and not from allabolag.se, update the DB
                if company["url"] is not None and "allabolag.se" not in company["url"] :
                    logging.debug("Updating URL for %s to %s", company["name"], company["url"])
                    interface.update_url_for_company(company["org_nr"], company["url"])
                else:
                    logging.debug("No URL found for %s, or the url is to allabolag.se. Deleting from DB", company["name"])
                    interface.delete_company_from_db(company["org_nr"])

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    typer.run(main)
