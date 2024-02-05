import os
import logging
from dotenv import load_dotenv
from requests import Session
from requests_pkcs12 import Pkcs12Adapter
from definitions import ROOT_DIR

# TODO: 
# 1. Use _allowed check in every operation
# 2. Write tests
# 3. (?) Implement category support

load_dotenv(os.path.join(ROOT_DIR, '.env'))

class VariableDoesNotSupportOperation(Exception):
    pass

class DoesNotOwnVariable(Exception):
    pass

class SCBapi():
    """
    Wrapper for SCB NÄRA API.
    """
    def __init__(self) -> None:
        self.api_base = 'https://privateapi.scb.se/nv0101/v1/sokpavar'
        self.api_pass = os.getenv("API_PASS")
        self.owned_vars_from_api = {}
        self.variables_from_api = {}
        self.json = {
            "Företagsstatus":"1",
            "Registreringsstatus":"1",
            "variabler": [],
            "Kategorier": []
        }
        self.operator_map = {
            'Innehaller':self.contains,
            'ArLikaMed':self.equals,
            'BorjarPa':self.prefix,
            'FranOchMed':self.start_from,
            'TillOchMed':self.up_to,
            'Mellan':self.between,
            'Finns':self.exists,
            'FinnsInte':self.exists
        }
    
    def __str__(self):
        """
        Gives a list of owned variables and their available operators.
        """
        self.update_owned_vars()
        
        owned = {}
        for k,v in self.owned_vars_from_api.items():
            owned[k] = [o.__name__ for o in v]

        s = "Owned variable: [allowed operations]\n"
        s += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        for k,v in owned.items():
            s+=f"{k}: {v}\n"
        return s

    def _check_if_allowed(self, caller, var_list= None, var_dict = None):
        """
        """
        if var_list is not None:
            for var in var_list:
                if var not in self.owned_vars_from_api:
                    raise DoesNotOwnVariable
                if caller not in self.owned_vars_from_api[var]:
                    raise VariableDoesNotSupportOperation
        if var_dict is not None:
            for var in var_dict.keys():
                if var not in self.owned_vars_from_api:
                    raise DoesNotOwnVariable
                if caller not in self.owned_vars_from_api[var]:
                    raise VariableDoesNotSupportOperation

    def update_variables(self):
        """
        Update the dictionary of all variables.
        The dictionary is in the format:
            {'variable_name':[allowed operations]}
            Where allowed_operations are:
                'contains',                       # Innehaller
                'equals',                         # ArLikaMed
                'prefix',                         # BorjarPa
                'starting' ( at incl.),           # FranOchMed
                'ending' (at incl.),              # TillOchMed
                'between'                         # Mellan
                'exists'                          # Finns, FinnsInte
        """
        self.variables_from_api = {}
        variables = self.get_request("api/Je/Variabler").json()
        for var in variables:
            self.variables_from_api[var['Id_Variabel_JE']]=var['Operatorer']

    def update_owned_vars(self):
        """
        Update the list of owned variables.
        The dictionary is in the format:
            {'variable_name':[callback functions]}
            Where callback functions are:
                'contains',                       # Innehaller
                'equals',                         # ArLikaMed
                'prefix',                         # BorjarPa
                'starting' ( at incl.),           # FranOchMed
                'ending' (at incl.),              # TillOchMed
                'between'                         # Mellan
                'exists'                          # Finns, FinnsInte
        """
        self.update_variables()

        owned_vars_list = []
        r = self.get_request("api/Je/KoptaVariabler").json()
        for var in r['Variabler']:
            owned_vars_list.append(var['Id_Variabel_JE'])
        
        self.owned_vars_from_api = {}
        for var in owned_vars_list:
            operators = self.variables_from_api[var]
            self.owned_vars_from_api[var] = [self.operator_map[o] for o in operators]
    
    def exists(self, var: list, exists: bool = True):
        """
        Method for creating a request that checks if a variable exists.
        
        :param var: the variable(s) to be checked.
        :param exists: boolean value for if the variable should exist or not.
        :returns: the object itself.
        """
        for v in var:
            variable_dict = {
                "Varde1": "",
                "Varde2": "",
                "Operator": "Finns" if exists else "FinnsInte",
                "Variabel": v
            }
            self.json["variabler"].append(variable_dict)
        return self
    
    def contains(self, var: dict):
        """
        Method for creating a request that checks if a variable contains provided information.
        
        :param var: Dictionary of variables and their values to be checked.
    
        :returns: the object itself.
        """
        for v in var:
            variable_dict = {
                "Varde1": var[v],
                "Varde2": "",
                "Operator": "Innehaller",
                "Variabel": v
            }
            self.json["variabler"].append(variable_dict)
        return self
    
    def equals(self, var: dict):
        """
        Method for creating a request that checks if a variable equals provided information.
        
        :param var: Dictionary of variables and their values to be checked.
        :returns: the object itself.
        """
        for v in var:
            variable_dict = {
                "Varde1": var[v],
                "Varde2": "",
                "Operator": "ArLikaMed",
                "Variabel": v
            }
            self.json["variabler"].append(variable_dict)
        return self
    
    def prefix(self, var: dict):
        """
        Method for creating a request that checks if a variable is prefixed with provided information.
        
        :param var: Dictionary of variables and their values to be checked.
        :returns: the object itself.
        """
        for v in var:
            variable_dict = {
                "Varde1": var[v],
                "Varde2": "",
                "Operator": "BorjarPa",
                "Variabel": v
            }
            self.json["variabler"].append(variable_dict)
        return self
    
    def start_from(self, var: dict):
        """
        Method for creating a request that checks all companies with a number variable starting with (incl.) the provided number.
        
        :param var: Dictionary of variables and their values to be checked.
        :returns: the object itself.
        """
        for v in var:
            variable_dict = {
                "Varde1": var[v],
                "Varde2": "",
                "Operator": "FranOchMed",
                "Variabel": v
            }
            self.json["variabler"].append(variable_dict)
        return self
    
    def up_to(self, var: dict):
        """
        Method for creating a request that checks all companies with a number variable up to (incl.) to the provided number.
        
        :param var: Dictionary of variables and their values to be checked.
        :returns: the object itself.
        """
        for v in var:
            variable_dict = {
                "Varde1": var[v],
                "Varde2": "",
                "Operator": "TillOchMed",
                "Variabel": v
            }
            self.json["variabler"].append(variable_dict)
        return self
    
    def between(self, var: dict):
        """
        Method for creating a request that checks all companies with a number variable between with the provided numbers.
        
        :param var: Dictionary of variables and their values to be checked.
        :returns: the object itself.
        """
        for key, value in var:
            variable_dict = {
                "Varde1": value[0],
                "Varde2": value[1],
                "Operator": "Mellan",
                "Variabel": key
            }
            self.json["variabler"].append(variable_dict)
        return self
    
    def sni(self, codes: list, level: int = 1, exclusion: bool = False):
        """
        Method for creating a request that checks all companies of the specified SNI sector codes.
        
        :param sni: List of SNI codes to be checked.
        :param exclusion: Boolean value for if the SNI codes should be excluded or not.
        :param level: The level of the SNI code to be checked. (1-3)
        """
        if exclusion:
            with open(f'{ROOT_DIR}/assets/sni.txt', 'r') as f:
                read_codes = f.read().splitlines()
            codes = [code for code in read_codes if code not in codes]
        
        category_dict = {
            "Kategori": "Bransch",
            "Kod": codes,
            "Branschniva": level
        }
        self.json["Kategorier"].append(category_dict)
        return self
    
    def fetch(self, address: str = "api/Je/HamtaForetag"):
        logging.debug('Sending the following request:\n%s', self.json)
        r = self.fetch_data(address, self.json)
        return r
    
    def fetch_data(self, r_address, body=None):
        """
        General method for creating requests against SCB API.
        
        :param r_address: the suffix of the address of the specific request.
        :param body: the body to be sent with POST requests
        :returns: a response object
        """
        with Session() as s:
            s.mount(self.api_base, Pkcs12Adapter(pkcs12_filename=f'{ROOT_DIR}/key.pfx', pkcs12_password=self.api_pass))
            if (body is None):   
                r = s.get(f'{self.api_base}/{r_address}') # En request
            else :
                r = s.post(f'{self.api_base}/{r_address}', json=body)
        return r

    def post_request(self, r_address, body):
        """
        Method for creating a POST request against SCB API.
        
        :param r_address: the suffix of the address of the specific request.
        :param body: the body to be sent with POST requests
        :returns: response object from the request. 
        """
        r = self.fetch_data(r_address, body)
        return r

    def get_request(self, r_address):
        """
        Method for creating a GET request against SCB API.
        
        :param r_address: the suffix of the address of the specific request.
        :returns: response object from the request. 
        """
        r = self.fetch_data(r_address)
        return r

#api.exists(["telefon", "email"]).contains({ "telefon": "070", "email": "a@b.c" }).fetch()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    scb = SCBapi()
    #print(scb)
    #scb.update_variables()
    #scb.exists(["telefon", "email"]).contains({ "telefon": "070", "email": "x@x.x" }).exists(["namn"]).fetch()
    r = scb.exists(["Telefon"]).start_from({"Antal arbetsställen": 4}).sni(["62010", "62020"]).fetch()
    print(r.json())
    