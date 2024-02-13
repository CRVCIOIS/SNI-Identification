import os
import json
import logging
from scripts.scb_wrapper import SCBapi
from definitions import ROOT_DIR 

def list_codes():
    """
    Get the list of all 5-digit codes which are not filtered by "filtered_sni.json".
    Saves as the list as two json files:
    - temp/SNI_to_name.json
    - temp/name_to_SNI.json

    :returns a tuple of dictionaries: (SNI_to_name, name_to_SNI)
    """
    wrapper = SCBapi()
    r = wrapper.get("api/Je/KategorierMedKodtabeller")

    with open(os.path.join(ROOT_DIR, 'assets', 'filtered_sni.json') , 'r', encoding='utf-8') as f:
        sni = json.load(f)
        sni_list = [sni_code['Varde'] for sni_code in sni[0]['VardeLista']]

    SNI_to_name = {}
    name_to_SNI = {} 

    for code in r.json()[1]['VardeLista']:
        if code['Varde'][0:2] in sni_list:
            SNI_to_name[code['Varde']] = code['Text']
            name_to_SNI[code['Text']] = code['Varde']

    if not os.path.exists(os.path.join(ROOT_DIR, 'temp')):
        os.makedirs(os.path.join(ROOT_DIR, 'temp'))

    with open(os.path.join(ROOT_DIR, 'temp', 'SNI_to_name.json'), 'w', encoding='utf-8') as f:
        json.dump(SNI_to_name, f, ensure_ascii=False)

    with open(os.path.join(ROOT_DIR, 'temp', 'name_to_SNI.json'), 'w', encoding='utf-8') as f:
        json.dump(name_to_SNI, f, ensure_ascii=False)

    return (SNI_to_name, name_to_SNI)

def get_municipalities():
    """
    Get the list of all municipalities from SCB.
    Saves as the list as two json files:
    - temp/code_to_municipalities.json
    - temp/municipalities_to_code.json

    :returns a tuple of dictionaries: (code_to_municipalities, municipalities_to_code)
    """
    wrapper = SCBapi()
    r = wrapper.get("api/Je/KategorierMedKodtabeller")

    code_to_municipalities = {}
    municipalities_to_code = {}

    if not os.path.exists(os.path.join(ROOT_DIR, 'temp')):
        os.makedirs(os.path.join(ROOT_DIR, 'temp'))

    for code in r.json()[4]['VardeLista']:
        code_to_municipalities[code['Varde']] = code['Text']
        municipalities_to_code[code['Text']] = code['Varde']

    with open(os.path.join(ROOT_DIR, 'temp', 'code_to_municipalities.json'), 'w', encoding='utf-8') as f:
        json.dump(code_to_municipalities, f, ensure_ascii=False)
    with open(os.path.join(ROOT_DIR, 'temp', 'municipalities_to_code.json'), 'w', encoding='utf-8') as f:
        json.dump(municipalities_to_code, f, ensure_ascii=False)

    return (code_to_municipalities, municipalities_to_code)

def load_codes():
    """
    Load the list of all 5-digit codes which are not filtered by "filtered_sni.json" from files.

    :returns a tuple of dictionaries: (SNI_to_name, name_to_SNI)
    """
    with open(os.path.join(ROOT_DIR, 'temp', 'SNI_to_name.json') , 'r', encoding='utf-8') as f:
        SNI_to_name = json.load(f)
    with open(os.path.join(ROOT_DIR, 'temp', 'name_to_SNI.json') , 'r', encoding='utf-8') as f:
        name_to_SNI = json.load(f)

    return (SNI_to_name, name_to_SNI)

def get_companies_by_codes():
    wrapper = SCBapi()
    # Däckservice = 45204
    for mun_code in get_municipalities()[0].keys():
        r = wrapper.sni(['45204']).category([mun_code]).count(False).json()
        print(f"Municipality: {mun_code} - Companies: {r}")


#TODO: Randomize the order of municipalities and count the number of companies fetched for each sni by municipality
#TODO: Stop fetching from SNI when the number of companies fetched is greater than 50


if __name__ == "__main__":
    #logging.basicConfig(level=logging.DEBUG)
    #list_codes()
    #get_municipalities()
    #get_companies_by_codes()

    wrapper = SCBapi()
    results = wrapper.sni(['45204']).category(['0181'], cat="SätesKommun").fetch().json()
    for company in results:
        print(company)
        input()
        name = company['Företagsnamn']
        print(name)
        branches = [company[x] for x in company.keys() if ('Bransch_' in x and 'kod' in x) and ('P' not in x and 'HAE' not in x)]
        print(branches)
        input()