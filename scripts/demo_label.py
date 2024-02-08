import json
import logging
from pathlib import Path
import typer


def label_sni(
    sni_codes: Path = typer.Argument(..., exists=True, dir_okay=False), 
    input: Path = typer.Argument(..., exists=True, dir_okay=False), 
    output_file_path: Path = typer.Argument(..., exists=False, dir_okay=False)):
    """
    Labels the scraped data with SNI codes.
    
    :param sni_codes: Path to the file with the SNI codes.
    :param input: Path to the file with the scraped data.
    :param output_file_path: Path to the file where the labeled data will be saved.
    """
    input = open_file(input)
    sni_codes = open_file(sni_codes)
    if (sni_codes and input) is not None:
        for item in input:
            if item["domain"] in sni_codes:
                item["SNI"] = sni_codes[item["domain"]]

        write_to_file(input, output_file_path)
        write_to_file(input, Path("assets/docs_nace_eval.json"))
  
def open_file(file_path):
    """
    Opens a JSON file and returns its contents as a dictionary.
    
    :param file_path: Path to the JSON file.
    :return: Dictionary containing the contents of the JSON file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("File not found: %s", file_path)
    except json.JSONDecodeError:
        logging.error("File is not a valid JSON file: %s", file_path)
    return None

def write_to_file(output_data, output_json_file_path):
    """
    Writes data to a JSON file.
    
    :param output_data: Data to be written to the file.
    :param output_json_file_path: Path to the output JSON file.
    """
    with open(Path(output_json_file_path), 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
    logging.info("Data written to %s", output_json_file_path)


if __name__ == '__main__':
   typer.run(label_sni)