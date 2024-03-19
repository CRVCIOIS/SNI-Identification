"""
Provides an adapter for SCB-related information in MongoDB
"""

import json
import logging
import os
import random
import tldextract

from definitions import ROOT_DIR
from classes.mongo import DBInterface, Schema
from classes.scb_api_wrapper import SCBapi

class SCBAdapter(DBInterface):
    """
    Class for interfacing with the SCB API and the MongoDB database.

    Example usage:
            ```
            scb = SCBAdapter()
            scb.fetch_companies_from_api(
                sni_start="00000",
                sni_stop="02300", 
                fetch_limit=10)
            ```
    """
    def __init__(self, init_api = False):
        """
        :param init_api: if True, then will call the initialization 
            scripts for the api wrapper. 
            Requires SCB credentials!
        """
        super().__init__()
        if init_api:
            self.init_api()

    def init_api(self):
        """
        Creates an SCB API wrapper, and then checks if the 3 collections 
            (SNI codes, municipalities and legal forms)  
            that are necessary for limiting the size of the API responses
            are empty, and in that case fetches the info from the API and saves
            the results into the DB.

            Requires SCB credentials! 
        """
        self.wrapper = SCBapi()
        self._init_collection(Schema.SNI, self._store_codes)
        self._init_collection(Schema.MUNICIPALITIES, self._store_municipalities)
        self._init_collection(Schema.LEGAL_FORMS, self._store_legal_forms)

    def _store_codes(self):
        """
        Saves the list of all 5-digit codes which are not filtered by "filtered_sni.json" to the mongodb database.
        The codes are saved inside the collection "SNI_codes".
        """

        with open(os.path.join(ROOT_DIR, 'assets', 'sni_include_list.json') , 'r', encoding='utf-8') as f:
            sni = json.load(f)
        
        self.mongo_client[Schema.DB][Schema.SNI].insert_many(sni)
        self.mongo_client[Schema.DB][Schema.SNI].create_index('sni_code')

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

    def _fetch_municipalities(self):
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
        
        with open(os.path.join(ROOT_DIR, 'assets', 'legal_forms_include_list.json') , 'r', encoding='utf-8') as f:
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
        
    def _fetch_legal_forms(self):
        """
        Fetch the list of all legal forms from the mongodb database.

        :returns a dict: {code: name}
        """
        forms = self.mongo_client[Schema.DB][Schema.LEGAL_FORMS].find()
        legal_forms = {}
        for form in forms:
            legal_forms[form['code']] = form['description']
        return legal_forms

    def _last_code_checked(self):
        """
        Last SNI code checked in the companies collection.
        
        returns:
        last SNI code checked
        """
        last_company = self.mongo_client[Schema.DB][Schema.COMPANIES].find().sort([("_id", -1)]).limit(1) # Get the last company entered into the database

        lc = list(last_company)
        if not list(lc):
            return None
        if "branch_codes" in lc[0]:
            return lc[0]["branch_codes"][0]
        return None    

    def _filter_companies(self, companies):
        """
        Filters information about companies fetched from the SCB API.
        
        params:
        companies: list of companies
        returns:
        list of filtered companies
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

    def _fetch_companies_by_municipality(self, sni_code: str, fetch_limit = 50):
        """
        Function for fetching companies by SNI code from random municipalities.
        
        params:
        sni_code: SNI code
        fetch_limit: maximum number of companies to fetch
        returns:
        list of companies
        """
        
        total_fetched = 0
        comp_arr = []
        logging.debug(f"Fetching from SNI: {sni_code}")

        mun_codes = list(self._fetch_municipalities().keys())
        random.shuffle(mun_codes)

        legal_forms = list(self._fetch_legal_forms().keys())

        while (total_fetched < fetch_limit) and (mun_codes):

            mun_code = mun_codes.pop()
            found_count = self.wrapper.sni([sni_code]).category([mun_code]).category(legal_forms, "Juridisk form").count(False)
            logging.debug(f"Municipality: {mun_code} - Companies: {found_count}")

            if found_count+total_fetched > fetch_limit:
                logging.debug(f"Skipping {mun_code} too many companies!")
                continue

            total_fetched += found_count
            companies = self.wrapper.sni([sni_code]).category([mun_code]).category(legal_forms, "Juridisk form").fetch().json()
            comp_arr.extend(self._filter_companies(companies))

        logging.debug(f"Total companies fetched: {total_fetched}")
        logging.debug(f"----> Stopping fetching from SNI {sni_code}")
        self._update_api_request_count(total_fetched)
        return comp_arr

    def _fetch_companies_from_api(self, start_sni, stop_sni, fetch_limit=50):
        """
        Fetch companies from the SCB API from random municipalities in the specified SNI code range.
        
        params:
        start_sni: start SNI code
        stop_sni: stop SNI code
        fetch_limit: maximum number of companies to fetch
        """
        last_code = self._last_code_checked()
        docs = self.mongo_client[Schema.DB][Schema.SNI].find({"sni_code": { "$ne": last_code }}).sort([("sni_code")])
        if (last_code is not None) and (last_code > start_sni):
            start_sni = last_code
        for doc in docs:
            if (doc["sni_code"] >= start_sni) and not (doc["sni_code"] > stop_sni):
                companies = self._fetch_companies_by_municipality(
                    doc["sni_code"], 
                    fetch_limit=fetch_limit)
                if len(companies) > 0:
                    self.mongo_client[Schema.DB][Schema.COMPANIES].insert_many(companies)
        self.wrapper.session.close()

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

    def fetch_all_companies_from_api(self, fetch_limit=50):
        """
        Fetch companies based on filtered SNI list from the SCB API from random municipalities.

        params:
        fetch_limit: maximum number of companies to fetch
        """
        start_sni="01120"
        stop_sni="95290"
        
        self._fetch_companies_from_api(start_sni, stop_sni, fetch_limit=fetch_limit)

    def _update_api_request_count(self, num_requests=1):
        """
        Updates the count of API requests made to the SCB API.
        params:
        num_requests: number of requests made
        """
        self.mongo_client[Schema.DB][Schema.API_COUNT].update_one({}, {"$inc": {"count": num_requests}}, upsert=True)
        
    def fetch_companies_from_db_by_sni(self, sni_code, has_url="BOTH"):
        """
        Fetch companies from the database based on the SNI code.
        :params sni_code:
        :param has_url:
            if "BOTH" then will return companies with and without urls
            if "ONLY" then will only return companies with urls 
                (that have non-whitespace characters)
            if "NO"   then will only return companies with missing urls 
                or with urls that only contain whitespaces
            will be returned.
        returns a list of companies:
        """
        match has_url.upper():
            case "ONLY":
                query = {"branch_codes": sni_code, "url": {"$regex": r"^\S+$"}}
            case "NO":
                query = {
                    "branch_codes": sni_code,
                    "$or":[
                        {"url": {"$exists": False}},
                        {"url": {"$regex": r"^\s*$"}}
                    ]
                }
            case _: # BOTH is default
                query = {"branch_codes": sni_code}

        companies = self.mongo_client[Schema.DB][Schema.COMPANIES].find(query)
        return list(companies)

    def fetch_all_companies_from_db(self, has_url="BOTH"):
        """
        Fetch all companies from the database.
        :param has_url:
            if "BOTH" then will return companies with and without urls
            if "ONLY" then will only return companies with urls 
                (that have non-whitespace characters)
            if "NO"   then will only return companies with missing urls 
                or with urls that only contain whitespaces
            will be returned.
        :returns a list of companies:
        """
        match has_url.upper():
            case "ONLY":
                query = {"url": {"$regex": r"^\S+$"}}
            case "NO":
                query = {
                    "$or":[
                        {"url": {"$exists": False}},
                        {"url": {"$regex": r"^\s*$"}}
                    ]
                }
            case _: # BOTH is default
                query = {}
        companies = self.mongo_client[Schema.DB][Schema.COMPANIES].find(query)
        return list(companies)

    def update_url_for_company(self, org_nr, url):
        """
        Updates the URL for a company in the database.
        params:
        org_nr: organization number
        url: URL to update
        """
        self.mongo_client[Schema.DB][Schema.COMPANIES].update_one({"org_nr": org_nr}, {"$set": {"url": url}})

    def _get_company_by_url(self, url):
        """
        Get company by URL.
        params:
        url: URL
        returns:
        company
        """
        return self.mongo_client[Schema.DB][Schema.COMPANIES].find_one({"url": {"$regex": url}})

    def get_company_by_url(self, url, try_base_domain = True):
        """
        Will try to find the company in the DB based on its URL.

        :param url:
        :try_base_domain: will search for the base domain if True and can't find the FQDN.

        :returns a PyMongo result object or None:
        """
        url_components = tldextract.extract(url)
        # Try to find the company using the full domain subdomain.domain.tld
        company = self._get_company_by_url(url_components.fqdn)

        # If not found, try using the base domain domain.tld
        if company is None and try_base_domain:
            base_domain = f"{url_components.domain}.{url_components.suffix}"
            company = self._get_company_by_url(base_domain)

        return company

    def fetch_company_by_org_nr(self, org_nr):
        """
        Fetch company from the database by organization number.
        params:
        org_nr: organization number
        returns:
        company
        """
        return self.mongo_client[Schema.DB][Schema.COMPANIES].find_one({"org_nr": org_nr})

    def delete_company_from_db(self, org_nr):
        """
        Deletes a company from the database based on the organization number.
        params:
        org_nr: organization number
        """
        self.mongo_client[Schema.DB][Schema.COMPANIES].delete_one({"org_nr": org_nr})

    def aggregate_companies_by_sni(self):
        """
        Fetches aggregate companies by SNI (Standard Industrial Classification) code.
        Returns:
            A list of dictionaries where each dictionary contains the following
            keys: 
                - _id: SNI code
                - companies: list of company ids (MongoDB ObjectIds)
                - count: number of companies
        """
        aggregate = self.mongo_client[Schema.DB][Schema.COMPANIES].aggregate(
            [{
                    '$match': {
                        'url': {
                        '$regex': '\\S'
                        }
                    }
                }, {
                    '$group': {
                        '_id': {
                            '$arrayElemAt': [
                                '$branch_codes', 0
                            ]
                        }, 
                        'companies': {
                            '$push': '$_id'
                        }, 
                        'count': {
                            '$count': {}
                        }
                    }
                }])
        return list(aggregate)

    def fetch_company_by_id(self, id):
        """
        Fetch company from the database by MongoDB ObjectId.
        :param id: MongoDB ObjectId
        :returns company:
        """
        return self.mongo_client[Schema.DB][Schema.COMPANIES].find_one({"_id": id})
