"""
Provides an adapter for scraping-related information in MongoDB.
"""
from classes.mongo import DBInterface, Schema

class ScrapeAdapter(DBInterface):
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
        self.mongo_client[Schema.DB][Schema.SCRAPED_DATA].create_index('company_id')
        self.mongo_client[Schema.DB][Schema.SCRAPED_DATA].create_index('timestamp')