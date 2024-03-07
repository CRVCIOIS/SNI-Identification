"""
Provides an adapter for extraction-related information in MongoDB.
"""
from classes.mongo import DBInterface, Schema

class ExtractAdapter(DBInterface):
    """
    Class for interfacing with the SCB API and the MongoDB database.

    Example usage:
            ```
            scb = SCBinterface()
            scb.fetch_companies_from_api(
                sni_start="00000",
                sni_stop="02300", 
                fetch_limit=10)
            ```
    """

    def __init__(self):
        super().__init__()
        self.mongo_client[Schema.DB][Schema.EXTRACTED_DATA].create_index('scraped_id')

    def fetch_company_extracted_data(self, id):
        """
        Fetch scraped data for a company from the database.
        params:
        id: MongoDB ObjectId
        returns:
        scraped data for the company
        """
        company = self.mongo_client[Schema.DB][Schema.EXTRACTED_DATA].find({"company_id": id}).sort({"_id":-1}).limit(1)
        company = list(company)
        if len(company) == 0:
            return None
        return company[0]
    
    def insert_extracted_data(self, extracted_data, url, company_id, timestamp, methods):
        """
        Inserts extracted data into the database.
        
        :param extracted_data (str): The extracted data.
        :param url (str): The URL of the extracted data.
        :param company_id: The object id of the company.
        :param timestamp:
        :param methods: A list of booleans [extract_meta,extract_body,p_only]
        """

        self.mongo_client[Schema.DB][Schema.EXTRACTED_DATA].update_one(
                {
                    'company_id':company_id,
                    'date':timestamp
                },   
                {
                    "$push": 
                    {
                        "data" : {'url':url,'method':methods,'data':extracted_data}
                    }
                } 
            ,
            upsert=True)