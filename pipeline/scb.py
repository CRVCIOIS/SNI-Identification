"""
Polls SCB
"""
from pathlib import Path
from adapters.scb import SCBAdapter

if __name__ == "__main__":
    from aux_functions.logger_config import conf_logger
    conf_logger({Path(__file__).stem})
    scb = SCBAdapter(init_collections=True)
    scb.fetch_all_companies_from_api(fetch_limit=50)