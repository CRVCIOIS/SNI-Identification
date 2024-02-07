import os
import pytest
from requests import Session
from requests_pkcs12 import Pkcs12Adapter
from dotenv import load_dotenv
from definitions import ROOT_DIR
import scripts.scb as scb
load_dotenv(os.path.join(ROOT_DIR, '.env'))


@pytest.fixture
def api():
    api = scb.SCBapi()
    return api

def test_exists(api):
    api.exists(["Telefon"])
    assert api.json["variabler"] == [{"Varde1":"",  "Varde2": "", "Operator":"Finns", "Variabel":"Telefon"}]
    api.reset_json()

    
def test_contains(api):
    api.contains({"Namn":"SSAB"})
    assert api.json["variabler"] == [{"Varde1":"SSAB",  "Varde2": "", "Operator":"Innehaller", "Variabel":"Namn"}]
    api.reset_json()

    
def test_equals(api):
    api.equals({"Antal arbetsställen":3})
    assert api.json["variabler"] == [{"Varde1":3,  "Varde2": "", "Operator":"ArLikaMed", "Variabel":"Antal arbetsställen"}]
    api.reset_json()

    
def test_prefix(api):
    api.prefix({"Telefon":"070"})
    assert api.json["variabler"] == [{"Varde1":"070",  "Varde2": "", "Operator":"BorjarPa", "Variabel":"Telefon"}]
    api.reset_json()


def test_start_from(api):
    api.start_from({"Antal arbetsställen":2})
    assert api.json["variabler"] == [{"Varde1":2,  "Varde2": "", "Operator":"FranOchMed", "Variabel":"Antal arbetsställen"}]
    api.reset_json()

    
def test_up_to(api):
    api.up_to({"Antal arbetsställen":3})
    assert api.json["variabler"] == [{"Varde1":3,  "Varde2": "", "Operator":"TillOchMed", "Variabel":"Antal arbetsställen"}]
    api.reset_json()


def test_between(api):
    api.between({"Antal arbetsställen":[2, 3]})
    assert api.json["variabler"] == [{"Varde1":2,  "Varde2": 3, "Operator":"Mellan", "Variabel":"Antal arbetsställen"}]
    api.reset_json()
    
    
def test_sni(api):
    api.sni(["62010"], 3)
    assert api.json["Kategorier"] == [{"Kategori":"Bransch", "Kod":["62010"], "Branschniva": 3}]
    api.reset_json()

    
def test_fetch(api):
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
    
    