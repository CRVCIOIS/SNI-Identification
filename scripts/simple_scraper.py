"""
"""
import requests
import json
import os
import tldextract
from datetime import datetime
import logging
import typer
import tempfile
from urllib.parse import urlparse
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
        self.follow_queries = {"om", "about"}
        self.headers = {"Accept-Language": "sv-SE,sv;"}
        self.filter = {"/en/", "/en-US", "/en-GB", ".pdf", ".jpg", ".png",
                       ".jpeg", ".gif", ".svg", ".doc", ".docx", ".ppt", ".pptx",
                       "cookies", "integritet","privacy", "policy", "terms",
                       "conditions", "contact", "job", "career", "press", "news",
                       "investor", "investors", "kontakt", "karriär", "jobb",}
        self.already_scraped = set()
       
    def scrape_all(self, follow_links=False, filter_=False):
        """
        Scrapes all urls in start_urls and saves each page in a json file.
        """
        self.urls = self._get_companies_from_db()
        self._get_already_scraped()
        
        for company in self.urls:
            if filter_:
                if self._check_filter(company):
                    continue
                
            if company['url'] in self.already_scraped:
                logging.debug("Already scraped %s", company['url'])
                continue
            
            logging.debug('Scraping %s', company['url'])
            try:
                request = self._request(company['url'])
            except Exception as e:
                logging.error('Failed to fetch %s: %s', company['url'], e)
                continue
            
            tld_extractor = tldextract.extract(company['url'])
            domain = f"{tld_extractor.domain}.{tld_extractor.suffix}"
            data = {'org_nr': company['org_nr'], 'url':company['url'], 'raw_html':request.text}
            timestamp = datetime.now().strftime('%Y-%m-%dT%H%M%S')
            self._save_to_json(data, f"{tld_extractor.domain}_{tld_extractor.suffix}_{timestamp}.json")
            
            if company["depth"] < 1 and follow_links:
                self._follow_links(request, domain, company) 
    
    def scrape_one(self, url):
        """
        Scrapes one url and saves the page in a temp json file.
        """
        try:
            request = self._request(url)
        except Exception as e:
            logging.error('Failed to fetch %s: %s', url, e)
            return
        tld_extractor = tldextract.extract(url)
        data = {'url':url, 'raw_html':request.text}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            logging.info('Saved scraped data to %s', f.name)
            name = f.name
        return name
        
    def prune_data(self):
        """
        Removes all data from the scraped_data folder that contains any of the filter words.
        """
        path = Path(ROOT_DIR) / "scraped_data"
        for filename in Path.iterdir(path):
            with open(Path(path, filename), 'r', encoding='utf-8') as f:
                file = json.load(f)
                for filter in self.filter:
                    if filter in urlparse(file['url']).path:
                        f.close()
                        filename.unlink()
                        logging.debug("Filtering out %s, matched with %s", file['url'], filter)
                        break

    def _save_to_json(self, data, filename):
        logging.info('Saving scraped data from %s', data['url'])
        Path('scraped_data').mkdir(parents=True, exist_ok=True)
        full_path = os.path.join('scraped_data',filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            self.already_scraped.add(data['url'])

    def _request(self, url):
        r = requests.get(url, timeout=5, headers=self.headers)
        return r
    
    def _check_filter(self, company):
        for filter in self.filter:
            if filter in urlparse(company['url']).path:
                logging.debug("Filtering out %s, matched with %s", company['url'], filter)
                return True
        return False
    
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
                if  (query in urlparse(link).path) and (link_domain == domain) and (link not in already_found) and (link not in self.already_scraped) and (link != company['url']):
                    logging.debug('Found link: %s', link)
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
    

    
def main(follow_links: Annotated[bool, typer.Argument(help="If true, the scraper will follow links on the start pages.")] = False,
         filter_: Annotated[bool, typer.Argument(help="If true, the scraper will filter out certain urls.")] = False):
    scraper = SimpleScraper()
    scraper.scrape_all(follow_links, filter_)
    logging.info("Scraping finished!")

if __name__ == "__main__":
    log_path = Path(ROOT_DIR) / "logs"
    log_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%dT%H%M%S')
    file_name = f"{Path(__file__).stem}_{timestamp}.log"
    logging.basicConfig(
                    filename=Path(log_path, file_name),
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
    typer.run(main)
    