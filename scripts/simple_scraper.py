"""
"""
import requests
import json
import os
import tldextract
import datetime
import logging
from pathlib import Path

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
    
            raw = self._request(url).text
            tld_extractor = tldextract.extract(url)
            domain = f"{tld_extractor.domain}.{tld_extractor.suffix}"

            data = {'domain':domain,'url':url,'raw_html':raw}

            self._save_to_json(data, f"{tld_extractor.domain}_{tld_extractor.suffix}_{timestamp}.json")