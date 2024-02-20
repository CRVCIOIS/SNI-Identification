
import json
import logging
import subprocess
from pathlib import Path

import typer
from typing_extensions import Annotated



def main(
        input_path: Annotated[Path, typer.Argument(
            exists=True, 
            file_okay=True, 
            dir_okay=False, 
            readable=True, 
            resolve_path=True, 
            formats=["json"], 
            help="The path to the input data file."
            )],
           output_path_dev_set: Annotated[Path, typer.Argument(
            exists=True, 
            file_okay=True, 
            dir_okay=False, 
            readable=True, 
            resolve_path=True, 
            formats=["json"], 
            help="The path to the output data file."
            )],
            nr_of_each_SNI: Annotated[int, typer.Argument()] = 10
        ):

        
        with open(input_path, 'r', encoding='utf-8') as f:
            logging.debug("Reading data from %s", input_path)
            data = json.load(f)

        SNI_counter: dict[str, int] = {}
        data_to_return = []

        # Loop over all companies in the dataset
        for company in data:
            #If the SNI code of the company is not added in to the SNI_counter or is less then the SNI counter max value (nr_of_each_SNI), then add it to the new smaller dataset add increment the SNI_counter for that specific SNI code
            if SNI_counter[company["SNI"]] is None or SNI_counter[company["SNI"]] < nr_of_each_SNI:
                data_to_return.append(company)
                if SNI_counter[company["SNI"]] is None:
                    SNI_counter[company["SNI"]] = 1
                else:
                    SNI_counter[company["SNI"]] = SNI_counter[company["SNI"]] + 1
                data.remove(company)
       

        #Write the modified dataset to file
        with open(input_path, 'w') as f:
            logging.debug("Overriding the file at '%s', with the new dataset", [input_path])
            json.dump(input_path, f, indent=4, ensure_ascii=False)
        #write the cross-validation dataset to file
        with open(output_path_dev_set, 'w') as f:
            logging.debug("Writing cross-validation data set to '%s'", [output_path_dev_set])
            json.dump(output_path_dev_set, f, indent=4, ensure_ascii=False)
             
            
             
      
   
if __name__ == "__main__":
    typer.run(main)