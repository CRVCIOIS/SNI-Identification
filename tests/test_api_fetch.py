"""
"""
import pytest
import validators.url.url as is_url
import regex as re


def is_sni(s):
    """
    Checks if a string is EXACTLY in the correct SNI-format (dd.dd.dddd).
    :param s: a string
    :returns: True if s is EXACTLY in the correct SNI-format (dd.dd.dddd)
    """
    sni_regex = re.compile(r'\b\d\d.\d\d.\d\d\d\d\b') 
    # Matches a string in EXACTLY the form dd.dd.dddd

    return sni_regex.match(s)

#is_url(URL) # returns True if URL

@pytest.fixture
def request():
    raise NotImplementedError

@pytest.fixture
def example_data():
    return {
        "url": "",
        "sni": "",
        "namn": ""
    }

def test_api_request(request, example_data):
    
    #Call function with request here:
    #result = api(request)
    
    # Assert that the result is the same as the data we expect
    # assert result == example_data
    raise NotImplementedError