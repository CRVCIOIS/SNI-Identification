"""
Tests for postprocess.
Input: List of dictionaries with the following keys: url, domain, raw_html.
Output: List of dictionaries with the following keys: domain, text.
It uses the pytest library to run the tests. To run simply execute the following command in the terminal:
> pytest tests/test_psotprocess.py
"""
import requests
from pathlib import Path
from scripts.postprocess import postprocess
import pytest
import tldextract
import json

@pytest.fixture
def urls():
    """
    Return a list of website urls to test against.
    """
    return ['https://ssab.se/','https://www.ssab.com/sv-se/kontakt', 'https://lkab.com/']

@pytest.fixture
def temp_input_file(tmp_path, urls):
    """
    Create a temporary input file containing a list of dictionaries with website information.
    The file has the same structure as the output from the scraper.
    """
    lst = []
    for url in urls:
        lst.append({'domain': tldextract.extract(url).domain, 'url': url, 'raw_html': requests.get(url).text})
    
    input_file = tmp_path / "input.json"
    with open(Path(input_file), 'w', encoding='utf-8') as f:
        json.dump(lst, f, indent=4, ensure_ascii=False)
        return input_file
    

def test_structure(tmp_path, temp_input_file):
    """
    Test the structure of the output file generated by the postprocess function.
    """
    temp_output_file = tmp_path / "output.json"
    postprocess(temp_input_file, temp_output_file, extract_meta=True, extract_body=False, p_only=False)
    
    with open(temp_output_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert isinstance(data, list)
    assert isinstance(data[0], dict) and isinstance(data[1], dict)
    assert len(data) == 2
    assert 'domain' in data[0] and isinstance(data[0]['domain'], str)
    assert 'SNI' in data[0] and isinstance(data[0]['SNI'], str)
    assert 'text' in data[0] and isinstance(data[0]['text'], str)
    assert 'domain' in data[1] and isinstance(data[1]['domain'], str)
    assert 'SNI' in data[1] and isinstance(data[1]['SNI'], str)
    assert 'text' in data[1] and isinstance(data[1]['text'], str)
    
    
    
    temp_input_file.unlink() # delete the temp file
    temp_output_file.unlink() # delete the temp file
    