"""
This script divides a dataset into a smaller dataset and a cross-validation dataset based on the SNI code of each company.

The smaller dataset will contain a percentage of companies with the same SNI code.
"""
import math

import typer
from typing_extensions import Annotated

from scripts.scb import SCBinterface


def main(
            procentage: Annotated[int, typer.Argument()] = 10
        ):
    """
    Divide the dataset into a smaller dataset and a cross-validation dataset based on the SNI code of each company.
    
    
    :param: procentage (int, optional): Procentage of the dataset that should be used for cross-validation. Defaults to 10%.
    """
    
    interface = SCBinterface()
    
    nr_of_each_SNI = interface.fetch_aggegrate_companies_by_sni()
    
    for sni in nr_of_each_SNI:
        nr_of_cross_validation_companies = math.floor(sni["count"] * procentage / 100)
        
        for index, company in enumerate(sni['companies']):
            company_scraped_data = interface.fetch_company_extracted_data(company)
            company_scraped_data["branch_codes"] = company["branch_codes"]
            if index <= nr_of_cross_validation_companies:
                #Move scraped data to cross-validation dataset
                interface.insert_to_dev_set(company_scraped_data)
            else:
                interface.insert_to_train_set(company_scraped_data)
                
 
   
if __name__ == "__main__":
    typer.run(main)