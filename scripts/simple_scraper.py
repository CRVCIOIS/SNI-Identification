"""
"""
import requests
import json
import os
import tldextract
import datetime
import logging
import typer
from requests_html import HTMLSession
from typing_extensions import Annotated
from pathlib import Path
from scripts.mongo import get_client, Schema
from definitions import ROOT_DIR

class SimpleScraper():
    """
    A simple synchronous "scraper" that fetches the content of a list of pages
        and saves it to json files.
    Example usage:
            scraper = SimpleScraper(['http://bdx.se','http://ssab.se'])
            scraper.scrape_all()
    """
    def __init__(self):
        self.urls = []
        self.follow_queries = {"/om","/om-oss", "/about"}
        self.headers = {"Accept-Language": "sv-SE,sv;"}
        self.filter = {"/en/", "/en-US", "/en-GB", ".pdf", ".jpg", ".png",
                       ".jpeg", ".gif", ".svg", ".doc", ".docx", ".ppt", ".pptx",
                       "cookies", "integritet","privacy", "policy", "terms",
                       "conditions", "contact", "job", "career", "press", "news",
                       "investor", "investors", "kontakt", "karriär", "jobb",}
        self.already_scraped = set()

    def _save_to_json(self, data, filename):
        logging.info('Saving scraped data to %s', filename)
        Path('scraped_data').mkdir(parents=True, exist_ok=True)
        full_path = os.path.join('scraped_data',filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            self.already_scraped.add(data['url'])

    def _request(self, url):
        r = requests.get(url, timeout=5, headers=self.headers)
        return r
    
    def _get_already_scraped(self):
        """
        Fetches all already scraped urls and returns them as a set.
        """
        path = Path(ROOT_DIR) / "scraped_data"
        for filename in Path.iterdir(path):
            with open(Path(path, filename), 'r', encoding='utf-8') as f:
                self.already_scraped.add(json.load(f)['url'])
                logging.debug("Added %s to already_scraped", filename)
    
    def _get_companies_from_db(self):
        """
        Fetches all companies from the database and returns them as a list of dictionaries.
        """
        client = get_client()
        query = {"url": {"$regex": r"/\S"}}
            
        logging.debug("Querying the database with the following query: %s", query)
        documents = client[Schema.DB][Schema.COMPANIES].find(query)
        companies = [{"org_nr": company['org_nr'], "url": company["url"], "depth": 0} for company in documents]
        return companies

    def scrape_all(self, follow_links=False):
        """
        Scrapes all urls in start_urls and saves each page in a json file.
        """
        self.urls = self._get_companies_from_db()
        self._get_already_scraped()
        
        for company in self.urls:
            for filter in self.filter:
                if filter in company['url']:
                    logging.debug("Filtering out %s", company['url'])
                    continue
                
            if company['url'] in self.already_scraped:
                logging.debug("Already scraped %s", company['url'])
                continue
            
            logging.info('Scraping %s', company['url'])
            timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')
            try:
                request = self._request(company['url'])
            except Exception as e:
                logging.error('Failed to fetch %s: %s', company['url'], e)
                continue
            tld_extractor = tldextract.extract(company['url'])
            domain = f"{tld_extractor.domain}.{tld_extractor.suffix}"
            data = {'org_nr': company['org_nr'], 'url':company['url'], 'raw_html':request.text}

            self._save_to_json(data, f"{tld_extractor.domain}_{tld_extractor.suffix}_{timestamp}.json")
            if company["depth"] < 1 and follow_links:
                self._follow_links(request, domain, company)
            
    def _follow_links(self, request, domain, company):
        """
        Follows all links on a page and adds them to start_urls if they match the follow_queries.
        """
        links = self._find_all_links(request)
        already_found = set()
        for link in links:
            tld_extractor = tldextract.extract(link)
            link_domain = f"{tld_extractor.domain}.{tld_extractor.suffix}"
            
            for query in self.follow_queries:
                if  (query in link) and (link_domain == domain) and (link not in already_found) and (link not in self.already_scraped) and (link != company['url']):
                    logging.info('Found link: %s', link)
                    self.urls.append({'org_nr': company['org_nr'], 'url': link, "depth": company["depth"] + 1})
                    already_found.add(link)     
                    
    def _find_all_links(self, request):
        """
        Finds all links on a page and returns them as a set.
        """
        try:
            session = HTMLSession()
            response = session.get(request.url)
            links = response.html.absolute_links
        except Exception as e:
            logging.error('Failed to fetch links: %s', e)
            return set()
        return links
    
    def prune_data(self):
        """
        Removes all data from the scraped_data folder that contains any of the filter words.
        """
        path = Path(ROOT_DIR) / "scraped_data"
        for filename in Path.iterdir(path):
            with open(Path(path, filename), 'r', encoding='utf-8') as f:
                file = json.load(f)
                for filter in self.filter:
                    if filter in file['url']:
                        f.close()
                        filename.unlink()
                        logging.info("Deleted %s", filename)
                        break
    
def main(follow_links: Annotated[bool, typer.Argument(help="If true, the scraper will follow links on the start pages.")] = False):
    scraper = SimpleScraper()
    scraper.scrape_all(follow_links)
    #scraper.prune_data()
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    typer.run(main)
    
    