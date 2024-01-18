"""
Tests for data extraction module.
Input: raw HTML file
Output: plaintext that contains information about the company - no HTML tags.
"""
import requests
import logging
from pathlib import Path
import regex as re
from extract import DataExtractor

def exist_tags_in_plaintext(text):
    """
    Check if the plaintext contains any HTML tags
    :param text: plaintext
    :returns: boolean
    """
    tag_re = re.compile(r'</?\s*[a-z-][^>]*\s*>|(\&(?:[\w\d]+|#\d+|#x[a-f\d]+);)')
    if tag_re.search(text) is None:
        return False
    return True

def test_tags(address, save_results = False):
    """
    Requests a URL, then runs following tests:
    - Check if tags exists in raw HTML; expected: True
    - Check if no tags in unfiltered, extracted data; expected: False
    - Check if no tags in filtered, extracted data; expected: False
    - Check if no tags in filtered, paragraph only, extracted data; expected: False
    """
    r = requests.get(address)
    extractor = DataExtractor()
    extractor.create_soup_from_html(r.text)

    s_unfiltered = extractor.extract(False)
    s_filtered = extractor.extract()
    s_p_only_filtered = extractor.extract(True,True)

    assert(exist_tags_in_plaintext(r.text))
    assert(not exist_tags_in_plaintext(s_unfiltered))
    assert(not exist_tags_in_plaintext(s_filtered))
    assert(not exist_tags_in_plaintext(s_p_only_filtered))

    logging.debug("All tests for %s ran successfully!", address)

    if save_results: # Can make debugging easier
        Path("extractor_output").mkdir(parents=True, exist_ok=True)
        with open('extractor_output/raw_html.txt','w', encoding='utf-8') as fp:
            fp.write(r.text)
        with open('extractor_output/unfiltered.txt','w', encoding='utf-8') as fp:
            fp.write(s_unfiltered)
        with open('extractor_output/filtered.txt','w', encoding='utf-8') as fp:
            fp.write(s_filtered)
        with open('extractor_output/p_only_filtered.txt','w', encoding='utf-8') as fp:
            fp.write(s_p_only_filtered)

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    addresses = ['https://ssab.se/', 'http://lkab.se','http://bdx.se']
    for address in addresses:
        test_tags(address, True)