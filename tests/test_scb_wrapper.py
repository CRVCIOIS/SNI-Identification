"""
Tests for SCB wrapper
"""
import os
import pytest
from requests import Session
from requests_pkcs12 import Pkcs12Adapter
from dotenv import load_dotenv
from definitions import ROOT_DIR
import classes.scb_api_wrapper as scb
load_dotenv(os.path.join(ROOT_DIR, '.env'))


@pytest.fixture
def api():
    """
    Fixture for creating an SCBapi object.

    :returns: an SCBapi object.
    """
    api = scb.SCBapi()
    return api
    
def test_exists(api):
    """
    Test case to check the behavior of the exists method in the API.

    Args:
        api: An instance of the API class.

    Raises:
        AssertionError: If the expected JSON response does not match the actual response.

    """
    api.exists(["Telefon"])
    assert api.json["variabler"] == [{"Varde1":"",  "Varde2": "", "Operator":"Finns", "Variabel":"Telefon"}]
    api.reset_json()

    
def test_contains(api):
    """
    Test case to verify the behavior of the 'contains' method in the API.

    Args:
        api: An instance of the API class.

    Raises:
        AssertionError: If the expected JSON response does not match the actual response.
    """
    api.contains({"Namn":"SSAB"})
    assert api.json["variabler"] == [{"Varde1":"SSAB",  "Varde2": "", "Operator":"Innehaller", "Variabel":"Namn"}]
    api.reset_json()

    
def test_equals(api):
    """
    Test case to verify the behavior of the 'equals' method in the API.

    Args:
        api: An instance of the API class.

    Raises:
        AssertionError: If the expected JSON response does not match the actual response.
    """
    api.equals({"Antal arbetsställen":3})
    assert api.json["variabler"] == [{"Varde1":3,  "Varde2": "", "Operator":"ArLikaMed", "Variabel":"Antal arbetsställen"}]
    api.reset_json()

    
def test_prefix(api):
    """
    Test case to verify the behavior of the 'prefix' method in the API.

    Args:
        api: An instance of the API class.

    Raises:
        AssertionError: If the expected JSON response does not match the actual response.
    """
    api.prefix({"Telefon":"070"})
    assert api.json["variabler"] == [{"Varde1":"070",  "Varde2": "", "Operator":"BorjarPa", "Variabel":"Telefon"}]
    api.reset_json()


def test_start_from(api):
    """
    Test case to verify the behavior of the 'start_from' method in the API.

    Args:
        api: An instance of the API class.

    Raises:
        AssertionError: If the expected JSON response does not match the actual response.
    """
    api.start_from({"Antal arbetsställen":2})
    assert api.json["variabler"] == [{"Varde1":2,  "Varde2": "", "Operator":"FranOchMed", "Variabel":"Antal arbetsställen"}]
    api.reset_json()

    
def test_up_to(api):
    """
    Test case to verify the behavior of the 'up_to' method in the API.

    Args:
        api: An instance of the API class.

    Raises:
        AssertionError: If the expected JSON response does not match the actual response.
    """
    api.up_to({"Antal arbetsställen":3})
    assert api.json["variabler"] == [{"Varde1":3,  "Varde2": "", "Operator":"TillOchMed", "Variabel":"Antal arbetsställen"}]
    api.reset_json()


def test_between(api):
    """
    Test case to verify the behavior of the 'between' method in the API.

    Args:
        api: An instance of the API class.

    Raises:
        AssertionError: If the expected JSON response does not match the actual response.
    """
    api.between({"Antal arbetsställen":[2, 3]})
    assert api.json["variabler"] == [{"Varde1":2,  "Varde2": 3, "Operator":"Mellan", "Variabel":"Antal arbetsställen"}]
    api.reset_json()
    
    
def test_sni(api):
    """
    Test case to verify the behavior of the 'sni' method in the API.

    Args:
        api: An instance of the API class.

    Raises:
        AssertionError: If the expected JSON response does not match the actual response.
    """
    api.sni(["62010"], 3)
    assert api.json["Kategorier"] == [{"Kategori":"Bransch", "Kod":["62010"], "Branschniva": 3}]
    api.reset_json()

    
def test_fetch(api):
    """
    Test case to verify the behavior of the 'fetch' method in the API. Compares a response from the API wrapper with a post to the SCB API.

    Args:
        api: An instance of the API class.

    Raises:
        AssertionError: If the wrapper response does not match the actual SCB API response.
    """
    resultWrapper = api.contains({"Namn": "SSAB EMEA AB"}).fetch().json()

    with Session() as s:
        body = {
            "Företagsstatus":"1",
            "Registreringsstatus":"1",
            "variabler": [{"Varde1":"SSAB EMEA AB",  "Varde2": "", "Operator":"Innehaller", "Variabel":"Namn"}],
            "Kategorier": []
        }
        s.mount('https://privateapi.scb.se/nv0101/v1/sokpavar', Pkcs12Adapter(pkcs12_filename=f'{ROOT_DIR}/key.pfx', pkcs12_password=os.getenv("API_PASS")))
        r = s.post(f'{"https://privateapi.scb.se/nv0101/v1/sokpavar"}/{"api/Je/HamtaForetag"}', json=body)
        resultPost = r.json()
    
    assert resultWrapper == resultPost

def test_check_if_allowed(api):
    """
    Tests for custom exceptions.
    Tries a non-existent variable, an unowned variable and unsupported operation.
    
    Args:
        api: An instance of the API class.

    Raises:
        AssertionError: If no exception is raised, or if the wrong exception is raised.
    """
    api.reset_json()
    
    # Test if Variable exists
    with pytest.raises(scb.VariableDoesNotExist):
        api.exists(["DoesNotExist"])
    
    # Test if Variable is not owned
    with pytest.raises(scb.DoesNotOwnVariable):
        api.exists(["E-post"])
    
    # Test if Variable does not support operation
    with pytest.raises(scb.VariableDoesNotSupportOperation):
        api.contains({"Postort": "Stockholm"})
    
    