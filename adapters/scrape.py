"""
Provides an adapter for scraping-related information in MongoDB.
"""
from classes.mongo import DBInterface, Schema

class ScrapeAdapter(DBInterface):
    """
    Performs operations on scraped data and the related mongo collections.
    Right now all it does is create indexes on two collections, 
        but is here for consistency with the rest of the modules.

    Example usage:
            ```
            scrape_adapter = ScrapeAdapter()
            ```
    """
    def __init__(self):
        super().__init__()
        self.mongo_client[Schema.DB][Schema.SCRAPED_DATA].create_index('company_id')
        self.mongo_client[Schema.DB][Schema.SCRAPED_DATA].create_index('timestamp')