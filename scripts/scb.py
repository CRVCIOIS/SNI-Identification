"""
Utility methods for fetching and saving results from the SCB API.
"""
import os
import json
import logging
import random
from enum import StrEnum
from scripts.scb_wrapper import SCBapi
from definitions import ROOT_DIR 
from scripts.mongo import get_client

# MongoDB definitions ("schema")

class Schema(StrEnum):
    """
    Used to loosely enforce a schema for MongoDB.
        Defines database name and collection names. 
    """
    # Database
    DB              = "SCB"
    # Collections
    SNI             = "SNI_codes"
    COMPANIES       = "companies"
    MUNICIPALITIES  = "municipalities"
    API_COUNT       = "api_count"
    LEGAL_FORMS     = "legal_forms"

class SCBinterface():
    """
    Class for interfacing with the SCB API and the MongoDB database.

    Example usage:
            ```
            scb = SCBinterface()
            scb.fetch_companies_from_api(
                sni_start="00000",
                sni_stop="02300", 
                fetch_limit=10,
                max_tries_per_code=5)
            ```
    """
    def __init__(self):
        self.wrapper = SCBapi()
        self.mongo_client = get_client()
        
        self._init_collection(Schema.SNI, self._store_codes)
        self._init_collection(Schema.MUNICIPALITIES, self._store_municipalities)
        self._init_collection(Schema.LEGAL_FORMS, self._store_legal_forms)

    def _init_collection(self, collection, callback):
        """
        Check if vital collections are empty, if so, store the data
        """
        if self.mongo_client[Schema.DB][collection].count_documents({}) == 0:
            callback()

    def _store_codes(self):
        """
        Saves the list of all 5-digit codes which are not filtered by "filtered_sni.json" to the mongodb database.
        The codes are saved inside the collection "SNI_codes".
        """
        
        r = self.wrapper.get("api/Je/KategorierMedKodtabeller")

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
        
        self.mongo_client[Schema.DB][Schema.SNI].insert_many(codes)
        self.mongo_client[Schema.DB][Schema.SNI].create_index('sni_code')

    def fetch_codes(self):
        """
        Fetch the list of all 5 digit codes from the mongodb database.
        
        :returns a dict: {sni_code: description}
        """
        
        codes = self.mongo_client[Schema.DB][Schema.SNI].find()
        sni_codes = {}
        for code in codes:
            sni_codes[code['sni_code']] = code['description']
        return sni_codes
        
    def _store_municipalities(self):
        """
        Saves the list of all municipalities from SCB to the db.
        """
        
        r = self.wrapper.get("api/Je/KategorierMedKodtabeller")
            
        municipalities = []
        for mun in r.json()[4]['VardeLista']:
            municipalities.append({
                'code': mun["Varde"],
                'name': mun["Text"]
            })

        self.mongo_client[Schema.DB][Schema.MUNICIPALITIES].insert_many(municipalities)
        self.mongo_client[Schema.DB][Schema.SNI].create_index('code')

    def fetch_municipalities(self):
        """
        Fetch the list of all municipalities from the mongodb database.
        
        :returns a dict: {code: name}
        """
        mun_list = self.mongo_client[Schema.DB][Schema.MUNICIPALITIES].find()
        municipalities = {}
        for m in mun_list:
            municipalities[m['code']] = m['name']
        return municipalities

    def _store_legal_forms(self):
        """
        Saves the list of all legal forms (that an entity can have), excluding those in the filter list from SCB to the db.
        """
        
        r = self.wrapper.get("api/Je/KategorierMedKodtabeller").json()
        
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
        
        self.mongo_client[Schema.DB][Schema.LEGAL_FORMS].insert_many(legal_forms)
        self.mongo_client[Schema.DB][Schema.LEGAL_FORMS].create_index('code')
        
    def fetch_legal_forms(self):
        """
        Fetch the list of all legal forms from the mongodb database.

        :returns a dict: {code: name}
        """
        forms = self.mongo_client[Schema.DB][Schema.LEGAL_FORMS].find()
        legal_forms = {}
        for form in forms:
            legal_forms[form['code']] = form['description']
        return legal_forms
        

    def last_code_checked(self):
        """
        Last SNI code checked in the companies collection.
        
        returns:
        last SNI code checked
        """
        last_company = self.mongo_client[Schema.DB][Schema.COMPANIES].find().sort([("_id", -1)]).limit(1) # Get the last company entered into the database
        
        if "branch_codes" in last_company[0]:
            return last_company[0]["branch_codes"][0]
        return None

    def _filter_companies(self, companies):
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
                    case "PostOrt":
                        filtered_company["postal_city"] = value
                    case "Säteskommun, kod":
                        filtered_company["municipality_code"] = value
                    case "Säteskommun":
                        filtered_company["municipality"] = value
                    case "Telefon":
                        filtered_company["phone"] = value
                if ('Bransch_' in key and 'kod' in key) and ('P' not in key and 'HAE' not in key):
                    filtered_company["branch_codes"].append(value)
            filtered_companies.append(filtered_company)
                    
        return filtered_companies

    def _fetch_companies_by_municipality(self, sni_code: str, fetch_limit = 50, max_tries_per_code = 15):
        """
        Function for fetching companies by SNI code from random municipalities.
        
        params:
        sni_code: SNI code
        fetch_limit: maximum number of companies to fetch
        max_tries_per_code: maximum number of tries to fetch companies from SNI code
        """
        
        total_fetched = 0
        tries = 0
        comp_arr = []
        logging.debug(f"Fetching from SNI: {sni_code}")

        mun_codes = list(self.fetch_municipalities().keys())
        random.shuffle(mun_codes)

        legal_forms = list(self.fetch_legal_forms().keys())

        while total_fetched < fetch_limit:
            if tries >= max_tries_per_code:
                logging.debug(f"Failed to fetch {sni_code} too many times, skipping!")
                break

            mun_code = mun_codes.pop()
            found_count = self.wrapper.sni([sni_code]).category([mun_code]).category(legal_forms, "Juridisk form").count(False).json()
            logging.debug(f"Municipality: {mun_code} - Companies: {found_count}")

            if found_count == 0:
                tries += 1
                continue
            if found_count+total_fetched > fetch_limit:
                logging.debug(f"Skipping {mun_code} too many companies!")
                tries += 1
                continue

            total_fetched += found_count
            companies = self.wrapper.sni([sni_code]).category([mun_code]).category(legal_forms, "Juridisk form").fetch().json()
            comp_arr.extend(self._filter_companies(companies))

        logging.debug(f"Total companies fetched: {total_fetched}")
        logging.debug(f"----> Stopping fetching from SNI {sni_code}")
        self._update_api_request_count(total_fetched)
        return comp_arr


    def fetch_companies_from_api(self, start_sni, stop_sni, fetch_limit=50, max_tries_per_code=15):
        """
        Fetch companies from the SCB API from random municipalities in the specified SNI code range.
        
        params:
        start_sni: start SNI code
        stop_sni: stop SNI code
        fetch_limit: maximum number of companies to fetch
        max_tries_per_code: maximum number of tries for each sni
        """
        last_code = self.last_code_checked()
        docs = self.mongo_client[Schema.DB][Schema.SNI].find({"sni_code": { "$ne": last_code }}).sort([("sni_code")])
        if (last_code is not None) and (last_code > start_sni):
            start_sni = last_code
        for doc in docs:
            if (doc["sni_code"] >= start_sni) and not (doc["sni_code"] > stop_sni):
                companies = self._fetch_companies_by_municipality(
                    doc["sni_code"], 
                    fetch_limit=fetch_limit, 
                    max_tries_per_code=max_tries_per_code)
                if len(companies) > 0:
                    self.mongo_client[Schema.DB][Schema.COMPANIES].insert_many(companies)
        

    def fetch_all_companies_from_api(self, fetch_limit=50):
        """
        Fetch companies based on filtered SNI list from the SCB API from random municipalities.

        params:
        fetch_limit: maximum number of companies to fetch
        """
        start_sni="01120"
        stop_sni="95290"
        
        self.fetch_companies_from_api(start_sni, stop_sni, fetch_limit=fetch_limit)
        

    def _update_api_request_count(self, num_requests=1):
        """
        Updates the count of API requests made to the SCB API.
        params:
        num_requests: number of requests made
        """
        self.mongo_client[Schema.DB][Schema.API_COUNT].update_one({}, {"$inc": {"count": num_requests}}, upsert=True)
        
    def fetch_companies_from_db(self, sni_code, no_url=False):
        """
        Fetch companies from the database based on the SNI code.
        params:
        sni_code: SNI code
        returns:
        list of companies
        """
        if no_url:
            query = {"branch_codes": sni_code, "url": {"$eq": ""}}
            companies = self.mongo_client[Schema.DB][Schema.COMPANIES].find(query)
        else:
            companies = self.mongo_client[Schema.DB][Schema.COMPANIES].find({"branch_codes": sni_code})
        return list(companies)


    def update_url_for_company(self, org_nr, url):
        """
        Updates the URL for a company in the database.
        params:
        org_nr: organization number
        url: URL to update
        """
        self.mongo_client[Schema.DB][Schema.COMPANIES].update_one({"org_nr": org_nr}, {"$set": {"url": url}})
