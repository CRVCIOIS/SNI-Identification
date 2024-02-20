import os
import json
import logging
import random
from scripts.scb_wrapper import SCBapi
from definitions import ROOT_DIR 
from scripts.mongo import get_client


# MongoDB definitions ("schema")
DB              = "SCB"
SNI             = "SNI_codes"
COMPANIES       = "companies"
MUNICIPALITIES  = "municipalities"

def store_codes():
    """
    Saves the list of all 5-digit codes which are not filtered by "filtered_sni.json" to the mongodb database.
    The codes are saved inside the collection "SNI_codes".
    """
    mongo_client = get_client()
    wrapper = SCBapi()
    r = wrapper.get("api/Je/KategorierMedKodtabeller")

    with open(os.path.join(ROOT_DIR, 'assets', 'filtered_sni.json') , 'r', encoding='utf-8') as f:
        sni = json.load(f)
        sni_list = [sni_code['Varde'] for sni_code in sni[0]['VardeLista']]
    
    codes = []
    
    for code in r.json()[1]['VardeLista']:
        if code['Varde'][0:2] in sni_list:
            codes.append({
                'sni_code':code['Varde'],
                'description': code['Text']
                })
    
    mongo_client[DB][SNI].insert_many(codes)
    mongo_client[DB][SNI].create_index('sni_code')

def fetch_codes(sni_to_description = True):
    """
    Fetch the list of all 5 digit codes from the mongodb database.
    
    :param sni_to_description: if False then {description: sni_code} will be returned
    :returns a list of touples: {sni_code: description}
    """
    
    mongo_client = get_client()
    codes = mongo_client[DB][SNI].find()
    sni_codes = {}
    if sni_to_description:
        for code in codes:
            sni_codes[code['sni_code']] = code['description']
    else:
        for code in codes:
            sni_codes[code['description']] = code['sni_code']
    return sni_codes
    
def store_municipalities():
    """
    Saves the list of all municipalities from SCB to the db.
    """
    wrapper = SCBapi()
    r = wrapper.get("api/Je/KategorierMedKodtabeller")
    
    mongo_client = get_client()
        
    municipalities = []
    for mun in r.json()[4]['VardeLista']:
        municipalities.append({
            'code': mun["Varde"],
            'name': mun["Text"]
        })

    mongo_client[DB][MUNICIPALITIES].insert_many(municipalities)
    mongo_client[DB][SNI].create_index('code')

def fetch_municipalities(code_to_name = True):
    """
    Fetch the list of all municipalities from the mongodb database.
    
    :param code_to_name: if False then return {name: code}
    :returns a list of touples: {code: name}
    """
    mongo_client = get_client()
    mun_list = mongo_client[DB][MUNICIPALITIES].find()
    municipalities = {}
    if code_to_name:
        for m in mun_list:
            municipalities[m['code']] = m['name']
    else:
        for m in mun_list:
            municipalities[m['name']] = m['code']
    return municipalities

def last_code_checked():
    """
    Last SNI code checked in the companies collection.
    
    params:
    companies: companies collection
    returns:
    last SNI code checked
    """
    mongo_client = get_client()
    last_company = mongo_client[DB][COMPANIES].find().sort([("_id", -1)]).limit(1) # Get the last company entered into the database
    if "sni_code" in last_company:
        return last_company["sni_code"]
    return None

def fetch_companies_by_municipality(sni_code: str, fetch_limit = 50, max_tries_per_code = 30):
    wrapper = SCBapi()
    fetch_count = 0
    tries = 0
    comp_arr = []
    print(f"Fetching from SNI: {sni_code}")
    
    mun_codes = list(fetch_municipalities().keys())
    random.shuffle(mun_codes)
    
    while fetch_count < fetch_limit and tries < max_tries_per_code:
        mun_code = mun_codes.pop()
        r = wrapper.sni([sni_code]).category([mun_code]).count(False).json()
        print(f"Municipality: {mun_code} - Companies: {r}")
        if r+fetch_count > fetch_limit:
            print(f"Skipping {mun_code} too many companies!")
            continue
        fetch_count += r
        companies = wrapper.sni([sni_code]).category([mun_code]).fetch().json()
        comp_arr.extend(companies)
    print(f"Total companies fetched: {fetch_count}")
    print(f"----> Stopping fetching from SNI {sni_code}")
    return comp_arr


def fetch_companies(start_sni, stop_sni):
    mongo_client = get_client()
    docs = mongo_client[DB][SNI].find().sort([("sni_code")])
    for doc in docs:
        if (int(doc["sni_code"]) >= int(start_sni)) and not (int(doc["sni_code"]) > int(stop_sni)):
            companies = fetch_companies_by_municipality(doc["sni_code"], fetch_limit=2)
            mongo_client[DB][COMPANIES].insert_many(companies)
            

def fetch_all_companies():
    """
    """
    start_sni="01120"
    stop_sni="95290"
    mongo_client = get_client()
    sni_codes = fetch_codes()
    
    last_code = last_code_checked()
    print(f"Last code checked: {last_code}")
    
    if last_code is not None:
        for code in sni_codes.keys():
            if code == last_code:
                sni_codes.pop(code)
                continue
            sni_codes.pop(code)



if __name__ == "__main__":
    #logging.basicConfig(level=logging.DEBUG)
    #list_codes()
    #get_municipalities()
    #get_companies_by_codes()
    mongo_client = get_client()
    if mongo_client[DB][SNI].count_documents({}) == 0:
        store_codes()
    if mongo_client[DB][MUNICIPALITIES].count_documents({}) == 0:
        store_municipalities()

    fetch_companies("01120", "01131")

    # wrapper = SCBapi()
    # results = wrapper.sni(['45204']).category(['0181'], cat="SätesKommun").fetch().json()
    # for company in results:
    #     print(company)
    #     input()
    #     name = company['Företagsnamn']
    #     print(name)
    #     branches = [company[x] for x in company.keys() if ('Bransch_' in x and 'kod' in x) and ('P' not in x and 'HAE' not in x)]
    #     print(branches)
    #     input()