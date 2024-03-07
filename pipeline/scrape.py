"""
Creates and runs scrapers.
"""
import logging
import typer
from annotated_types import Annotated
from pathlib import Path
from classes.scraper import Scraper
from adapters.scb import SCBAdapter

def main(
    scrape_output_folder: Path = typer.Argument(..., dir_okay=True),
    follow_links: Annotated[bool, typer.Argument(help="If true, the scraper will follow links on the start pages.")] = False,
    filter_: Annotated[bool, typer.Argument(help="If true, the scraper will filter out certain urls.")] = False):

    scb_adapter = SCBAdapter()

    logging.info("Started fetching companies from db...")
    companies = scb_adapter.fetch_all_companies_from_db(no_url=True)
    logging.info("Finished fetching companies from db...")
    start_urls = [{'label':company['org_nr'], 'url':company["url"]} for company in companies]

    logging.info("Started scraping...")
    scraper = Scraper(scrape_output_folder)
    scraper.scrape_all(start_urls,follow_links, filter_)
    logging.info("Finished scraping!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    typer.run(main)