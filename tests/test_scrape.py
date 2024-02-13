"""
Tests for Scrapy spider.
Input: url of a website.
Output: List of dictionaries with the following keys: url, domain, raw_html.

It uses the pytest library to run the tests. To run simply execute the following command in the terminal:
> pytest tests/test_scrape.py
"""

import subprocess
from pathlib import Path
import pytest
import requests
import json
import tldextract

ROOT_DIR = Path(__file__).resolve().parents[1] 

@pytest.fixture
def url():
    """
    Return a website address
    """
    return 'https://bdx.se/'


@pytest.fixture
def raw_request(url):
    """
    Return the raw HTML of a website
    """
    return requests.get(url).text


def test_scraping(url, raw_request):
    """
    Test the scraping functionality
    """
    temp_path = ROOT_DIR / "temp"
    temp_path.mkdir(exist_ok=True)
    temp_output_file = temp_path / "scrapy_test_output.json"
    command = f'scrapy parse {url} -c parse_item --spider=crawlingNLP -a start_urls="{url}" -o {temp_output_file}:json'.split(' ')
    subprocess.check_call(command, cwd=Path('scraping'))
    
    with open(temp_output_file, 'r', encoding='utf-8') as f:
        scraped_data = json.load(f)
        
    assert len(scraped_data) == 1    
    assert scraped_data[0]['url'] == url
    assert scraped_data[0]['domain'] ==  tldextract.extract(url).domain
    assert scraped_data[0]['raw_html'] == raw_request
   
    temp_output_file.unlink()
    temp_path.rmdir()
    