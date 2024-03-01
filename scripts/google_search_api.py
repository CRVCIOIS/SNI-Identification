"""
This module provides a class that interacts with the Google Custom Search API to perform searches.
"""
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv


load_dotenv()

class GoogleSearchAPI:
    """
    A class that interacts with the Google Custom Search API to perform searches.
    """

    def __init__(self):
        self.api_key = os.environ.get('GOOGLE_SEARCH_API_KEY')
        self.search_engine_id = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')

    def search(self, query):
        """
        Performs a search using the Google Custom Search API.

        Args:
            query (str): The search query.

        Returns:
            str: The URL of the first search result.
        """
        service = build("customsearch", "v1", developerKey=self.api_key)
        # hl: The language of the search results. gl: The country to search from. lr: The language to return results in. cr: The country to search in.
        res = service.cse().list(q=query, cx=self.search_engine_id, hl="sv", gl="sv", lr="lang_sv", cr="sv", num=1).execute()
        if res['items'] and 'link' in res["items"][0]:
            return res["items"][0]["link"]
        return ""
    
    def batch_search(self, query_list: list[str]):
        """
        Performs a batch search using the Google Custom Search API.

        Args:
            query_list (list[str]): A list of search queries.

        Returns:
            list[str]: A list of URLs corresponding to the first search result for each query.
        """
        results: list[str] = []
        for query in query_list:
            results.append(self.search(query))
        return results
    