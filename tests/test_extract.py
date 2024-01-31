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
    # Matches: 
    # HTML tags: everything that starts with < or </ and a letter, and ends with >
    # i.e. <div class ="1234">
    # HTML entities: everything that starts with & and a letter, and ends with ;
    # i.e. &nbsp;

    if tag_re.search(text) is None:
        return False
    return True

def test_tags(address, save_results = False):
    """
    Requests a URL, then runs following tests twice (once from string and once from file path):
    - Check if tags exists in raw HTML; expected: True
    - Check if no tags in unfiltered, extracted data; expected: False
    - Check if no tags in filtered, extracted data; expected: False
    - Check if no tags in filtered, paragraph only, extracted data; expected: False
    :param address: the address of the website to test against.
    :param save_results: if True then save the output of the extractor into "extractor_output" folder.
    """
    r = requests.get(address)
    Path("temp").mkdir(parents=True, exist_ok=True)
    with open('temp/website.html','w', encoding='utf-8') as fp:
        fp.write(r.text)

    extractor_string = DataExtractor()
    extractor_file_path = DataExtractor()
    extractor_string.create_soup_from_string(r.text)
    extractor_file_path.open_file('temp/website.html')

    for extractor, extractor_name in [(extractor_string, 'from_string'), (extractor_file_path, 'from_file')]:
        s_unfiltered = extractor.extract(False)
        s_filtered = extractor.extract()
        s_p_only_filtered = extractor.extract(True,True)

        assert(exist_tags_in_plaintext(r.text))
        assert(not exist_tags_in_plaintext(s_unfiltered))
        assert(not exist_tags_in_plaintext(s_filtered))
        assert(not exist_tags_in_plaintext(s_p_only_filtered))

        if save_results:
            Path("extractor_output").mkdir(parents=True, exist_ok=True)
            with open(f'extractor_output/{extractor_name}_raw_html.txt','w', encoding='utf-8') as fp:
                fp.write(r.text)
            with open(f'extractor_output/{extractor_name}_unfiltered.txt','w', encoding='utf-8') as fp:
                fp.write(s_unfiltered)
            with open(f'extractor_output/{extractor_name}_filtered.txt','w', encoding='utf-8') as fp:
                fp.write(s_filtered)
            with open(f'extractor_output/{extractor_name}_p_only_filtered.txt','w', encoding='utf-8') as fp:
                fp.write(s_p_only_filtered)
        
    logging.debug("All tests for %s ran successfully!", address)

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    addresses = ['https://ssab.se/', 'http://lkab.se','http://bdx.se']
    for address in addresses:
        test_tags(address, True)