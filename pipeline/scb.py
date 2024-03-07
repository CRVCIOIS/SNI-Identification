"""
Polls SCB
"""
import logging
from adapters.scb import SCBAdapter

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scb = SCBAdapter()
    scb.fetch_all_companies_from_api(fetch_limit=50)