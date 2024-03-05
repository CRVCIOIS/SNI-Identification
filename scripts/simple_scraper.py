"""
"""
import requests
import json
import os
import tldextract
import datetime
import logging
import typer
from pathlib import Path
from scripts.mongo import get_client, Schema

class SimpleScraper():
    """
    A simple synchronous "scraper" that fetches the content of a list of pages
        and saves it to json files.
    Example usage:
            scraper = SimpleScraper(['http://bdx.se','http://ssab.se'])
            scraper.scrape_all()
    """
    def __init__(self, start_urls):
        self.start_urls = start_urls

    def _save_to_json(self, data, filename):
        logging.info('Saving scraped data to %s', filename)
        Path('scraped_data').mkdir(parents=True, exist_ok=True)
        full_path = os.path.join('scraped_data',filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

    def _request(self, url):
        r = requests.get(url, timeout=5)
        return r

    def scrape_all(self):
        """
        Scrapes all urls in start_urls and saves each page in a json file.
        """
        for url in self.start_urls:
            logging.info('Scraping %s', url)
            timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')
            try:
                raw = self._request(url).text
            except requests.exceptions.ReadTimeout:
                logging.debug("Request timed out, continuing...")
                continue
            tld_extractor = tldextract.extract(url)
            domain = f"{tld_extractor.domain}.{tld_extractor.suffix}"

            data = {'domain':domain,'url':url,'raw_html':raw}

            self._save_to_json(data, f"{tld_extractor.domain}_{tld_extractor.suffix}_{timestamp}.json")
    
def main():
    client = get_client()
    query = {"url": {"$regex": r"/\S"}}
        
    logging.debug("Querying the database with the following query: %s", query)
    documents = client[Schema.DB][Schema.COMPANIES].find(query)
    start_urls = [company["url"] for company in documents]

    scraper = SimpleScraper(start_urls)
    scraper.scrape_all()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    typer.run(main)
    
    