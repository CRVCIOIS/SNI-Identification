"""
Creates and runs scrapers.
"""
import typer
from pathlib import Path
from classes.scraper import Scraper
from adapters.scb import SCBAdapter

def main(scrape_output_folder: Path = typer.Argument(..., dir_okay=True)):
    scb_adapter = SCBAdapter()

    companies = scb_adapter.fetch_all_companies_from_db(no_url=True)
    start_urls = [company["url"] for company in companies]

    scraper = Scraper(scrape_output_folder, start_urls)
    scraper.scrape_all()

if __name__ == "__main__":
    typer.run(main)