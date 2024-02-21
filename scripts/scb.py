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
API_COUNT       = "api_count"
LEGAL_FORMS     = "legal_forms"

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

def fetch_codes():
    """
    Fetch the list of all 5 digit codes from the mongodb database.
    
    :param sni_to_description: if False then {description: sni_code} will be returned
    :returns a list of touples: {sni_code: description}
    """
    
    mongo_client = get_client()
    codes = mongo_client[DB][SNI].find()
    sni_codes = {}
    for code in codes:
        sni_codes[code['sni_code']] = code['description']
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

def fetch_municipalities():
    """
    Fetch the list of all municipalities from the mongodb database.
    
    :param code_to_name: if False then return {name: code}
    :returns a list of touples: {code: name}
    """
    mongo_client = get_client()
    mun_list = mongo_client[DB][MUNICIPALITIES].find()
    municipalities = {}
    for m in mun_list:
        municipalities[m['code']] = m['name']
    return municipalities

def store_legal_forms():
    """
    Saves the list of all legal forms (that an entity can have), excluding those in the filter list from SCB to the db.
    """
    wrapper = SCBapi()
    r = wrapper.get("api/Je/KategorierMedKodtabeller").json()
    
    with open(os.path.join(ROOT_DIR, 'assets', 'filtered_legal_forms.json') , 'r', encoding='utf-8') as f:
        filter_list = json.load(f)
    
    filter_list = [form['Varde'] for form in filter_list]
    
    legal_forms = []
    
    for cat in r:
        if cat['Id_Kategori_JE'] == 'Juridisk form':
            for form in cat['VardeLista']:
                if form['Varde'] in filter_list:
                    legal_forms.append({
                        'code': form['Varde'],
                        'description': form['Text']
                    })
    
    mongo_client = get_client()
    mongo_client[DB][LEGAL_FORMS].insert_many(legal_forms)
    mongo_client[DB][LEGAL_FORMS].create_index('code')
    
def fetch_legal_forms():
    """
    Fetch the list of all legal forms from the mongodb database.
    
    :param code_to_name: if False then return {name: code}
    :returns a list of touples: {code: name}
    """
    mongo_client = get_client()
    forms = mongo_client[DB][LEGAL_FORMS].find()
    legal_forms = {}
    for form in forms:
        legal_forms[form['code']] = form['description']
    return legal_forms
    


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

def filter_companies(companies):
    """
    Filters information about companies fetched from the SCB API.
    
    params:
    companies: list of companies
    """
    filtered_companies = []
    for company in companies:
        filtered_company = {}
        filtered_company["branch_codes"] = []
        filtered_company["url"] = ""
        for key, value in company.items():
            match key:
                case "Företagsnamn":
                    filtered_company["name"] = value
                case "OrgNr":
                    filtered_company["org_nr"] = value
                case "PostAdress":
                    filtered_company["address"] = value
                case "PostNr":
                    filtered_company["postal_code"] = value
                case "SätesKommun, kod":
                    filtered_company["municipality_code"] = value
                case "SätesKommun":
                    filtered_company["municipality"] = value
                case "Telefon":
                    filtered_company["phone"] = value
            if ('Bransch_' in key and 'kod' in key) and ('P' not in key and 'HAE' not in key):
                filtered_company["branch_codes"].append(value)
        filtered_companies.append(filtered_company)
                
    return filtered_companies

def fetch_companies_by_municipality(sni_code: str, fetch_limit = 50, max_tries_per_code = 30):
    """
    Function for fetching companies by SNI code from random municipalities.
    
    params:
    sni_code: SNI code
    fetch_limit: maximum number of companies to fetch
    max_tries_per_code: maximum number of tries to fetch companies from SNI code
    """
    wrapper = SCBapi()
    fetch_count = 0
    tries = 0
    comp_arr = []
    print(f"Fetching from SNI: {sni_code}")
    
    mun_codes = list(fetch_municipalities().keys())
    random.shuffle(mun_codes)
    
    legal_forms = list(fetch_legal_forms().keys())
    
        
    while fetch_count < fetch_limit and tries < max_tries_per_code:
        mun_code = mun_codes.pop()
        r = wrapper.sni([sni_code]).category([mun_code]).category(legal_forms, "Juridisk form").count(False).json()
        print(f"Municipality: {mun_code} - Companies: {r}")
        if r == 0:
            tries += 1
            continue
        if r+fetch_count > fetch_limit:
            print(f"Skipping {mun_code} too many companies!")
            continue
        fetch_count += r
        companies = wrapper.sni([sni_code]).category([mun_code]).category(legal_forms, "Juridisk form").fetch().json()
        comp_arr.extend(filter_companies(companies))
    print(f"Total companies fetched: {fetch_count}")
    print(f"----> Stopping fetching from SNI {sni_code}")
    update_api_request_count(fetch_count)
    return comp_arr


def fetch_companies_from_api(start_sni, stop_sni, fetch_limit=50):
    """
    Fetch companies from the SCB API from random municipalities in the specified SNI code range.
    
    params:
    start_sni: start SNI code
    stop_sni: stop SNI code
    fetch_limit: maximum number of companies to fetch
    """
    mongo_client = get_client()
    docs = mongo_client[DB][SNI].find().sort([("sni_code")])
    for doc in docs:
        if (int(doc["sni_code"]) >= int(start_sni)) and not (int(doc["sni_code"]) > int(stop_sni)):
            companies = fetch_companies_by_municipality(doc["sni_code"], fetch_limit=fetch_limit)
            if len(companies) > 0:
                mongo_client[DB][COMPANIES].insert_many(companies)
            

def fetch_all_companies_from_api(fetch_limit=50):
    """
    Fetch companies based on filtered SNI list from the SCB API from random municipalities.
    """
    start_sni="01120"
    stop_sni="95290"
    
    fetch_companies_from_api(start_sni, stop_sni, fetch_limit=fetch_limit)
    

def update_api_request_count(num_requests=1):
    """
    Updates the count of API requests made to the SCB API.
    params:
    num_requests: number of requests made
    """
    mongo_client = get_client()
    mongo_client[DB][API_COUNT].update_one({}, {"$inc": {"count": num_requests}}, upsert=True)
    
def fetch_companies_from_db(sni_code = "01110"):
    """
    Fetch companies from the database based on the SNI code.
    params:
    sni_code: SNI code
    returns:
    list of companies
    """
    mongo_client = get_client()
    companies = mongo_client[DB][COMPANIES].find({"branch_codes": sni_code})
    return list(companies)


def update_url_for_company(org_nr, url):
    """
    Updates the URL for a company in the database.
    params:
    org_nr: organization number
    url: URL to update
    """
    mongo_client = get_client()
    mongo_client[DB][COMPANIES].update_one({"org_nr": org_nr}, {"$set": {"url": url}})
        


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
    if mongo_client[DB][LEGAL_FORMS].count_documents({}) == 0:
        store_legal_forms()

    #fetch_companies_from_api("01131", "01131", fetch_limit=2)
    
    print(fetch_companies_from_db("01131"))

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