"""
This script divides a dataset into a smaller dataset and a cross-validation dataset based on the SNI code of each company.

The smaller dataset will contain a percentage of companies with the same SNI code.
"""
import math

import typer
from typing_extensions import Annotated

from adapters.train import TrainAdapter
from adapters.extract import ExtractAdapter
from adapters.scb import SCBAdapter

def main(
            validation_set_size: Annotated[int, typer.Argument()] = 10
        ):
    """
    Divide the dataset into a smaller dataset and a validation dataset based on the SNI code of each company.

    :param: validation_set_size (int, optional): Percent of the entire dataset that should be used as a validation set. Defaults to 10%.
    """

    scb_adapter       = SCBAdapter()
    extract_adapter   = ExtractAdapter()
    train_adapter     = TrainAdapter()

    nr_of_each_SNI = scb_adapter.aggregate_companies_by_sni()
    
    stored_sni = {}
    
    for sni in nr_of_each_SNI:
        nr_of_cross_validation_companies = math.ceil(sni["count"] * validation_set_size / 100)
        
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
            else:
                train_adapter.insert_to_train_set(company_scraped_data)

if __name__ == "__main__":
    typer.run(main)