"""
This module contains test cases for the GoogleSearchAPI class.

The GoogleSearchAPI class provides methods to perform searches and batch searches using the Google Search API.

Test cases:
- test_search: Checks the behavior of the search method in the API.
- test_batch_search: Checks the behavior of the batch_search method in the API.
"""
import pytest
from classes.google_api_wrapper import GoogleSearchAPI
import tldextract


@pytest.fixture
def api():
    """
    Fixture for creating a GoogleSearchAPI object.

    Returns:
        GoogleSearchAPI: An instance of the GoogleSearchAPI class.
    """
    api = GoogleSearchAPI() 
    return api

def test_search(api):
    """
    Test case to check the behavior of the search method in the API.

    Args:
        api: An instance of the API class.

    Raises:
        AssertionError: If the expected URL does not match the actual URL.
    """
    res = api.search("LKAB")
    assert tldextract.extract(res).fqdn == "lkab.com"
    
def test_batch_search(api):
    """
    Test case to check the behavior of the batch_search method in the API.

    Args:
        api: An instance of the API class.

    Raises:
        AssertionError: If the expected list of URLs does not match the actual list of URLs.
    """
    res = api.batch_search(["FL Shipping AB", "LKAB"])
    assert tldextract.extract(res[0]).fqdn == "www.flshipping.se"
    assert tldextract.extract(res[1]).fqdn == "lkab.com"
    