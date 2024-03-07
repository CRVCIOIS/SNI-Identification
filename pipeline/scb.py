"""
Polls SCB
"""
from adapters.scb import SCBAdapter

if __name__ == "__main__":
    scb = SCBAdapter()
    scb.fetch_all_companies_from_api(fetch_limit=50)