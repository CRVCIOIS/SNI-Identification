"""
"""
import requests
import json
import os
import tldextract
from datetime import datetime
import logging
import tempfile
from urllib.parse import urlparse
from requests_html import HTMLSession
from pathlib import Path

class Scraper():
    """
    A simple synchronous crawler that crawls sites while propagating labels,
        and saves the results to json files.
    Can also scrape single pages and save them as temporary files.
    Example usage:
            scraper = SimpleScraper(['http://bdx.se','http://ssab.se'])
            scraper.scrape_all()
    """
    def __init__(self, scrape_output_folder):
        """
        :param scrape_output_folder: where to save scraped sites
        """
        self.scrape_output_folder = scrape_output_folder
        self.urls = []
        self.follow_queries = {"om", "about"}
        self.headers = {"Accept-Language": "sv-SE,sv;"}
        self.filter = {"/en/", "/en-US", "/en-GB", "lang=en", "in-english", ".pdf", ".jpg", ".png",
                       ".jpeg", ".gif", ".svg", ".doc", ".docx", ".ppt", ".pptx",
                       "cookies", "integritet","privacy", "policy", "terms",
                       "conditions", "contact", "job", "career", "press", "news",
                       "investor", "investors", "kontakt", "karriär", "jobb",
                       "styrelse", "nyhet", "medlemmar", "personal", "ledning",
                       "hallbarhet", "sustainability", "miljo", "environment",
                       "lediga-tjanster", "lediga-jobb", 
                       "visselblasning", "socialamedier", "social-media", "instagram",
                       "sociala-medier", "facebook", "twitter", "linkedin", "youtube",}
        self.already_scraped = set()

    def scrape_all(self, labeled_urls, follow_links=False, filter_=False):
        """
        Crawls all urls from start_urls and saves each page in a json file.
        :param labled_urls: a dictionary 
        """
        self.urls = [
            {
                "label":item['label'], 
                "url": item['url'], 
                "depth": 0
            } 
                for item in labeled_urls]

        self._get_already_scraped()

        for url in self.urls:
            if filter_:
                if self._check_filter(url):
                    continue

            if url['url'] in self.already_scraped:
                logging.debug("Already scraped %s", url['url'])
                continue

            logging.debug('Scraping %s', url['url'])
            try:
                request = self._request(url['url'])
            except Exception as e:
                logging.error('Failed to fetch %s: %s', url['url'], e)
                continue

            tld_extractor = tldextract.extract(url['url'])
            domain = f"{tld_extractor.domain}.{tld_extractor.suffix}"
            data = {'label':url['label'],'url':url['url'], 'raw_html':request.text}
            timestamp = datetime.now().strftime('%Y-%m-%dT%H%M%S')
            self._save_to_json(data, f"{tld_extractor.domain}_{tld_extractor.suffix}_{timestamp}.json")

            if url["depth"] < 1 and follow_links:
                self._follow_links(request, domain, url)

    def scrape_one(self, url):
        """
        Scrapes one url and saves the page in a temp json file.
        """
        try:
            request = self._request(url)
        except Exception as e:
            logging.error('Failed to fetch %s: %s', url, e)
            return

        data = {'url':url, 'raw_html':request.text}

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            logging.info('Saved scraped data to %s', f.name)
            name = f.name
        return name

    def prune_data(self):
        """
        Removes all data from the scrape_output_folder folder that contains any of the filter words.
        """
        path = Path(self.scrape_output_folder)
        for filename in Path.iterdir(path):
            with open(Path(path, filename), 'r', encoding='utf-8') as fd:
                f = json.load(fd)
                for filter_ in self.filter:
                    if filter_ in urlparse(f['url']).path:
                        fd.close()
                        filename.unlink()
                        logging.debug("Filtering out %s, matched with %s", f['url'], filter_)
                        break

    def _save_to_json(self, data, filename):
        logging.info('Saving scraped data from %s', data['url'])
        Path(self.scrape_output_folder).mkdir(parents=True, exist_ok=True)
        full_path = os.path.join(self.scrape_output_folder,filename)
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
            self.already_scraped.add(data['url'])

    def _request(self, url):
        r = requests.get(url, timeout=5, headers=self.headers)
        return r
    
    def _check_filter(self, url):
        for filter_ in self.filter:
            if filter_ in urlparse(url['url']).path:
                logging.debug("Filtering out %s, matched with %s", url['url'], filter_)
                return True
        return False
    
    def _get_already_scraped(self):
        """
        Fetches all already scraped urls and returns them as a set.
        """
        path = Path(self.scrape_output_folder)
        for filename in Path.iterdir(path):
            with open(Path(path, filename), 'r', encoding='utf-8') as f:
                self.already_scraped.add(json.load(f)['url'])
                logging.debug("Added %s to already_scraped", filename)

    def _follow_links(self, request, domain, url):
        """
        Follows all links on a page and adds them to urls if they match the follow_queries.
        """
        links = self._find_all_links(request)
        already_found = set()
        for link in links:
            tld_extractor = tldextract.extract(link)
            link_domain = f"{tld_extractor.domain}.{tld_extractor.suffix}"
            
            for query in self.follow_queries:
                if  (query in urlparse(link).path) and (link_domain == domain) and (link not in already_found) and (link not in self.already_scraped) and (link != url['url']):
                    logging.debug('Found link: %s', link)
                    self.urls.append({'label':url['label'],'url': link, "depth": url["depth"] + 1})
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
    