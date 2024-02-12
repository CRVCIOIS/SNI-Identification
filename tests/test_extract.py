"""
Tests for data extraction module.
Input: raw HTML file
Output: plaintext that contains information about the company - no HTML tags.

It uses the pytest library to run the tests. To run simply execute the following command in the terminal:
> pytest scripts/test_extract.py
"""
import requests
import logging
from pathlib import Path
import regex as re
from scripts.scripts.extract import DataExtractor, NoBeautifulSoupObject
import pytest

@pytest.fixture
def address():
    """
    Return a website address
    """
    return 'https://ssab.se/'

@pytest.fixture
def raw_request(address):
    """
    Return the raw HTML of a website
    """
    return requests.get(address).text

@pytest.fixture
def temp_input_file(tmp_path, raw_request):
    """
    Create a temp file from http request and return the file path
    """
    input_file = tmp_path / "request.html"
    input_file.write_text(raw_request, encoding='utf-8')
    return input_file
    

def exist_tags_in_plaintext(text):
    """
    Check if the plaintext contains any HTML tags
    :param text: plaintext
    :returns: boolean
    """
    tag_re = re.compile(r'</?\s*[a-z-][^>]*\s*>|(\&(?:[\w\d]+|#\d+|#x[a-f\d]+);)')
    # Matches: 
    # HTML tags: everything that starts with < or </ and a letter, and ends with >
    # i.e. <div class ="1234">
    # HTML entities: everything that starts with & and a letter, and ends with ;
    # i.e. &nbsp;

    if tag_re.search(text) is None:
        return False
    return True


def test_tags(raw_request, temp_input_file, save_results = True):
    """
    Requests a URL, then runs following tests twice (once from string and once from file path):
    - Check if tags exists in raw HTML; expected: True
    - Check if no tags in unfiltered, extracted data; expected: False
    - Check if no tags in filtered, extracted data; expected: False
    - Check if no tags in filtered, paragraph only, extracted data; expected: False
    :param address: the address of the website to test against.
    :param save_results: if True then save the output of the extractor into "extractor_output" folder.
    """

    extractor_string = DataExtractor()
    extractor_file_path = DataExtractor()
    extractor_string.create_soup_from_string(raw_request)
    extractor_file_path.open_file(temp_input_file)

    for extractor, extractor_name in [(extractor_string, 'from_string'), (extractor_file_path, 'from_file')]:
        s_unfiltered = extractor.extract(False)
        s_filtered = extractor.extract()
        s_p_only_filtered = extractor.extract(True,True)

        assert(exist_tags_in_plaintext(raw_request)), "Raw HTML should contain tags"
        assert(not exist_tags_in_plaintext(s_unfiltered)), "Unfiltered plaintext should not contain tags"
        assert(not exist_tags_in_plaintext(s_filtered)), "Filtered plaintext should not contain tags"
        assert(not exist_tags_in_plaintext(s_p_only_filtered)), "Filtered plaintext (paragraph only) should not contain tags"

        if save_results:
            Path("extractor_output").mkdir(parents=True, exist_ok=True)
            with open(f'extractor_output/{extractor_name}_raw_html.txt','w', encoding='utf-8') as fp:
                fp.write(raw_request)
            with open(f'extractor_output/{extractor_name}_unfiltered.txt','w', encoding='utf-8') as fp:
                fp.write(s_unfiltered)
            with open(f'extractor_output/{extractor_name}_filtered.txt','w', encoding='utf-8') as fp:
                fp.write(s_filtered)
            with open(f'extractor_output/{extractor_name}_p_only_filtered.txt','w', encoding='utf-8') as fp:
                fp.write(s_p_only_filtered)
        
    logging.debug("All tag tests for %s ran successfully!", address)
    temp_input_file.unlink() # delete the temp file

def test_simple_data(address, tel, email):
    """
    Test if the extractor can find a given telephone number and e-mail
    in the website address.
    :param address: the website's address.
    :param tel: the company's phone number. Give an empty string if no public info available.
    :param email: the company's e-mail. Give an empty string if no public info available.
    """
    r = requests.get(address)
    Path("temp").mkdir(parents=True, exist_ok=True)
    with open('temp/website.html','w', encoding='utf-8') as fp:
        fp.write(r.text)

    extractor = DataExtractor()
    extractor.open_file('temp/website.html')
    simple_data = extractor.extract_simple_data()

    if len(simple_data['tel']) == 0:
        simple_data['tel'].append('')
    if len(simple_data['e-mail']) == 0:
        simple_data['e-mail'].append('')

    assert(tel in simple_data['tel'])
    assert(email in simple_data['e-mail'])

    logging.debug("All simple data tests for %s ran successfully!", address)

def test_no_soup_object():
    """
    Check if the extractor raises correct error when trying to extract without a soup.
    """
    extractor = DataExtractor()
    try:
        extractor.extract()
        assert False
    except Exception as e:
        assert(type(e) is NoBeautifulSoupObject)

    try:
        extractor.extract_simple_data()
        assert False
    except Exception as e:
        assert(type(e) is NoBeautifulSoupObject)
    
    logging.debug("No soup test ran successfully!")

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    addresses = ['https://ssab.se/', 'http://lkab.se','http://bdx.se']
    tels = ['', '0771760000', '0920262600']
    emails = ['','info@lkab.com','info@bdx.se']

    for i, address in enumerate(addresses):
        test_tags(address, True)
        test_simple_data(address,tels[i],emails[i])

    test_no_soup_object()