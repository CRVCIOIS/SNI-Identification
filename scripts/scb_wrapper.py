"""
SCB API Wrapper and related exceptions.
"""
import os
import logging
import copy
import json
from dotenv import load_dotenv
from requests import Session
from requests_pkcs12 import Pkcs12Adapter
from definitions import ROOT_DIR

CERT_PATH = os.path.join(ROOT_DIR, "key.pfx")

load_dotenv(os.path.join(ROOT_DIR, '.env'))

class VariableDoesNotExist(Exception):
    """Variable does not exist in the list of all variables."""
    pass
class VariableDoesNotSupportOperation(Exception):
    """Variable does not support the chosen operation."""
    pass

class DoesNotOwnVariable(Exception):
    """Variable does not exist in the list of owned variables."""
    pass

class SCBapi():
    """
    Wrapper for SCB NÄRA API.
    
    To use the API, the user must have a valid certificate and a password.
    The password should be stored as an environment variable.
    
    Example usage:
    ```python
    scb = SCBapi()
    resultWrapper = api.up_to({"Antal arbetsställen": "4"}).sni(["62010"]).fetch().json()
    print(resultWrapper.json())
    ```
    
    :param cert_path: the path to the certificate file.
    """
    def __init__(self, cert_path=CERT_PATH) -> None:
        self.api_base = 'https://privateapi.scb.se/nv0101/v1/sokpavar'
        self.api_pass = os.getenv("SCB_API_PASS")
        self.cert_path = cert_path
        self.owned_vars_from_api = {}
        self.variables_from_api = {}
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
        self.default_json = {
            "Företagsstatus":"1",
            "Registreringsstatus":"1",
            "variabler": [],
            "Kategorier": []
        }
        self.json = {}
        self.update_owned_vars()
        self.reset_json()
    
    def __str__(self):
        """
        Owned variables + internal JSON file
        """
        s = "Variable: [allowed operations]\n"
        s += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        for k,v in self.variables_from_api.items():
            s+=f"{k}: {v}\n"
        s += "Owned variable: [allowed operations]\n"
        s += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        for k,v in self.owned_vars_from_api.items():
            s+=f"{k}: {v}\n"
        s += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        s += "Current JSON file:\n"
        s += "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
        s += json.dumps(self.json,indent=2, ensure_ascii=False)
        return s

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
        variables = self._get_request("api/Je/Variabler").json()
        for var in variables:
            self.variables_from_api[var['Id_Variabel_JE']]=var['Operatorer']

    def update_owned_vars(self):
        """
        Update the list of owned variables.
        The dictionary is in the format:
            {'variable_name':[function name]}
            Where the function names are:
                'contains',                       # Innehaller
                'equals',                         # ArLikaMed
                'prefix',                         # BorjarPa
                'starting' ( at incl.),           # FranOchMed
                'ending' (at incl.),              # TillOchMed
                'between'                         # Mellan
                'exists'                          # Finns, FinnsInte
        """
        if not self.variables_from_api:
            self.update_variables()

        owned_vars_list = []
        r = self._get_request("api/Je/KoptaVariabler").json()
        for var in r['Variabler']:
            owned_vars_list.append(var['Id_Variabel_JE'])
        
        self.owned_vars_from_api = {}
        for var in owned_vars_list:
            operators = self.variables_from_api[var]
            self.owned_vars_from_api[var] = [self.operator_map[o].__name__ for o in operators]
    
    def exists(self, var: list, exists: bool = True):
        """
        Method for creating a request that checks if a variable exists.
        
        :param var: the variable(s) to be checked.
        :param exists: boolean value for if the variable should exist or not.
        :returns: the object itself.
        """
        self._check_if_allowed('exists',var_list=var)

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
        self._check_if_allowed('contains',var_dict=var)
    
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
        self._check_if_allowed('equals',var_dict=var)

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
        self._check_if_allowed('prefix',var_dict=var)

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
        self._check_if_allowed('start_from',var_dict=var)

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
        self._check_if_allowed('up_to',var_dict=var)

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
        self._check_if_allowed('between',var_dict=var)

        for key, value in var.items():
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
        
        :param codes: List of SNI codes to be checked.
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
    
    def category(self, codes: list, cat="SätesKommun"):
        """
        Method for creating a request that checks all companies of the specified category codes.
        
        :param cat: The category to be checked.
        :param codes: List of category codes to be checked.
        """
        
        category_dict = {
            "Kategori": cat,
            "Kod": codes
        }
        self.json["Kategorier"].append(category_dict)
        return self
        
    
    def reset_json(self):
        """
        Sets the internal JSON file to the default values. 
        """
        self.json = copy.deepcopy(self.default_json)

    def fetch(self, address="api/Je/HamtaForetag", keep_json = False):
        """
        Sends a request with the current JSON file.

        :param keep_json: if True then will not reset the internal json.
        :returns: the response object.
        """
        logging.debug("Sending the following request to '%s':\n%s", address, self.json)
        r = self.fetch_data(address, self.json)
        if not keep_json:
            self.reset_json()
        return r
    
    def get(self, address):
        """
        Sends a GET request to the specified address.

        :param address: the address to send the request to.
        :returns: the response object.
        """
        logging.debug("Sending GET request to '%s'", address)
        r = self.fetch_data(address)
        return r
    
    def count(self, keep_json = True):
        """
        Sends a request with the current JSON file to the "count" endpoint.

        :param keep_json: if True then will not reset the internal json.
        :returns: the response object.
        """
        r = self.fetch("api/Je/RaknaForetag",keep_json)
        return r
    
    def fetch_data(self, r_address, body=None):
        """
        General method for creating requests against SCB API.
        
        :param r_address: the suffix of the address of the specific request.
        :param body: the body to be sent with POST requests
        :returns: a response object
        """
        with Session() as s:
            s.mount(self.api_base, Pkcs12Adapter(pkcs12_filename=self.cert_path, pkcs12_password=self.api_pass))
            if (body is None):   
                r = s.get(f'{self.api_base}/{r_address}') # En request
            else :
                r = s.post(f'{self.api_base}/{r_address}', json=body)
        return r

    def _post_request(self, r_address, body):
        """
        Method for creating a POST request against SCB API.
        
        :param r_address: the suffix of the address of the specific request.
        :param body: the body to be sent with POST requests
        :returns: response object from the request. 
        """
        r = self.fetch_data(r_address, body)
        return r

    def _get_request(self, r_address):
        """
        Method for creating a GET request against SCB API.
        
        :param r_address: the suffix of the address of the specific request.
        :returns: response object from the request. 
        """
        r = self.fetch_data(r_address)
        return r

    def _check_if_allowed(self, operator, var_list= None, var_dict = None):
        """
        Checks if the given variables are supported by the caller operation.

        :param operator: a string (the exact name of the caller function).
        :var_list: a list of variables used in the operation, or None.
        :var_dict: a dictionary used in the operation, or None.

        :raises VariableDoesNotExist: if the variable does not appear in the variable list fetched from the API.
        :raises DoesNotOwnVariable: if the user does not own the chosen variable.
        :raises VariableDoesNotSupportOperation: if the variable does not support the chosen operation (the caller).
        """
        if var_list is not None:
            for var in var_list:
                if var not in self.variables_from_api:
                    raise VariableDoesNotExist("'%s' does not exist in the list of all variables!" % (var))
                if var not in self.owned_vars_from_api:
                    raise DoesNotOwnVariable("'%s' exists, but is not in the list of owned variables!" % (var))
                if operator not in self.owned_vars_from_api[var]:
                    raise VariableDoesNotSupportOperation("'%s' does not support '%s'!" % (var, operator))

        if var_dict is not None:
            for var in var_dict.keys():
                if var not in self.variables_from_api:
                    raise VariableDoesNotExist("'%s' does not exist in the list of all variables!" % (var))
                if var not in self.owned_vars_from_api:
                    raise DoesNotOwnVariable("'%s' exists, but is not in the list of owned variables!" % (var))
                if operator not in self.owned_vars_from_api[var]:
                    raise VariableDoesNotSupportOperation("'%s' does not support '%s'!" % (var, operator))
