"""
This script divides a dataset into a smaller dataset and a cross-validation dataset based on the SNI code of each company.

The smaller dataset will contain a percentage of companies with the same SNI code.
"""
import logging
import math

import typer
from pathlib import Path
from typing_extensions import Annotated

from adapters.train import TrainAdapter
from adapters.extract import ExtractAdapter
from adapters.scb import SCBAdapter

def main(
            percentage_training_split: Annotated[int, typer.Argument()] = 70,
            percentage_eval_split: Annotated[int, typer.Argument()] = 20,
            percentage_test_split: Annotated[int, typer.Argument()] = 10,
        ):
    """
    Divide the dataset into a smaller dataset and a validation dataset based on the SNI code of each company.

    :param percentage_training_split (int, optional): 
        Percent of the entire dataset that should be used for training. 
        Defaults to 70%.
    :param percentage_eval_split (int, optional):
        Percent of the entire dataset that should be used for evaluation.
        Defaults to 20%.
    :param percentage_test_split (int, optional):
        Percent of the entire dataset that should be used for testing.
        Defaults to 10%.
    """
    
    if percentage_training_split + percentage_eval_split + percentage_test_split != 100:
        raise ValueError("The sum of the data split percentages must be 100.")

    scb_adapter       = SCBAdapter()
    extract_adapter   = ExtractAdapter()
    train_adapter     = TrainAdapter()

    nr_of_each_SNI = scb_adapter.aggregate_companies_by_sni()
    
    stored_sni = {}

    train_adapter.delete_all_data_sets()
    logging.debug("Deleted all previous data sets")
    
    for sni in nr_of_each_SNI:
        nr_of_cross_validation_companies = math.floor(
            sni["count"] * (percentage_eval_split) / 100)
        nr_of_test_companies = math.floor(sni["count"] * (percentage_test_split) / 100)
        
        for company in sni['companies']:
            company_scraped_data = extract_adapter.fetch_company_extracted_data(company)
            if company_scraped_data is None:
                continue
            company_scraped_data.pop("_id")
            
            company_data = scb_adapter.fetch_company_by_id(company)
            company_scraped_data["branch_codes"] = company_data["branch_codes"]
            if company_data["branch_codes"][0] not in stored_sni.keys()  or stored_sni[company_data["branch_codes"][0]] < nr_of_cross_validation_companies:
                #Move scraped data to cross-validation dataset
                train_adapter.insert_to_dev_set(company_scraped_data)
                if company_data["branch_codes"][0] not in stored_sni.keys():
                    stored_sni[company_data["branch_codes"][0]] = 1
                else:
                    stored_sni[company_data["branch_codes"][0]] += 1
            elif (stored_sni[company_data["branch_codes"][0]] <
                   nr_of_cross_validation_companies + nr_of_test_companies):
                #Move scraped data to test dataset
                train_adapter.insert_to_test_set(company_scraped_data)
                stored_sni[company_data["branch_codes"][0]] += 1
            else:
                train_adapter.insert_to_train_set(company_scraped_data)

    logging.info("Dataset division finished!")

if __name__ == "__main__":
    from aux_functions.logger_config import conf_logger
    conf_logger(Path(__file__).stem)
    typer.run(main)