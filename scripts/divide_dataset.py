"""
This script divides a dataset into a smaller dataset and a cross-validation dataset based on the SNI code of each company.

The smaller dataset will contain a percentage of companies with the same SNI code.
"""
import logging
import math
from datetime import datetime
import typer
from typing_extensions import Annotated
from pathlib import Path
from definitions import ROOT_DIR
from scripts.scb import SCBinterface


def main(
            percentage_train: Annotated[int, typer.Argument()] = 70,
        ):
    """
    Divide the dataset into a smaller dataset and a cross-validation dataset based on the SNI code of each company.
    
    :param: percentage_train (int, optional): Procentage of the dataset that should be used for training. Defaults to 70%.
    """
    
    interface = SCBinterface()
    nr_of_each_SNI = interface.fetch_aggegrate_companies_by_sni()
    stored_sni = {}
    
    for sni in nr_of_each_SNI:
        nr_of_cross_validation_companies = math.ceil(sni["count"] * (100 - 10 - percentage_train) / 100)
        nr_of_test_companies = math.ceil(sni["count"] * (10) / 100) # 10% of the companies will be used for test data
        logging.info(f"Number of companies with SNI code {sni['sni_code']}: {sni['count']}.")
        logging.info(f"Number of companies in cross-validation dataset: {nr_of_cross_validation_companies}.")
        logging.info(f"Number of companies in test dataset: {nr_of_test_companies}.")
        logging.info(f"Number of companies in training dataset: {sni['count'] - nr_of_cross_validation_companies - nr_of_test_companies}.")
        
        for company in sni['companies']:
            company_scraped_data = interface.fetch_company_extracted_data(company)
            if company_scraped_data is None:
                continue
            company_scraped_data.pop("_id")
            
            company_data = interface.fetch_company_by_id(company)
            company_scraped_data["branch_codes"] = company_data["branch_codes"]
            if company_data["branch_codes"][0] not in stored_sni.keys()  or stored_sni[company_data["branch_codes"][0]] < nr_of_cross_validation_companies:
                #Move scraped data to cross-validation dataset
                interface.insert_to_dev_set(company_scraped_data)
                if company_data["branch_codes"][0] not in stored_sni.keys():
                    stored_sni[company_data["branch_codes"][0]] = 1
                else:
                    stored_sni[company_data["branch_codes"][0]] += 1
            elif stored_sni[company_data["branch_codes"][0]] < nr_of_cross_validation_companies + nr_of_test_companies:
                #Move scraped data to test dataset
                interface.insert_to_test_set(company_scraped_data)
                stored_sni[company_data["branch_codes"][0]] += 1
            else:
                interface.insert_to_train_set(company_scraped_data)
                
 
   
if __name__ == "__main__":
    log_path = Path(ROOT_DIR) / "logs"
    log_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%dT%H%M%S')
    file_name = f"{Path(__file__).stem}_{timestamp}.log"
    logging.basicConfig(
                    filename=Path(log_path, file_name),
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)
    typer.run(main)
    logging.info("Dataset division finished!")