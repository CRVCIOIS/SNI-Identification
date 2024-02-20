import json
import logging
from pathlib import Path
import typer


def label(
    sni_path: Path = typer.Argument(..., exists=True, dir_okay=False), 
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False), 
    output_file_path: Path = typer.Argument(..., exists=False, dir_okay=False)):
    """
    Labels the scraped data with SNI codes.
    
    :param sni_path (Path): Path to the json file with the SNI codes, a dictionary: {'domain': 'SNI code'}.
    :param input_path (Path): Path to the file with the extracted data to be labeled.
    :param output_file_path (Path): Path to the file where the labeled data will be saved.
    """
    data = open_json(input_path)
    sni_codes = open_json(sni_path)
    if (sni_codes and data) is not None:
        for item in data:
            if item["domain"] in sni_codes:
                item["SNI"] = sni_codes[item["domain"]]

        write_to_json(data, output_file_path)
  
def open_json(file_path: Path):
    """
    Opens a JSON file and returns its contents as a JSON object.
    
    :param file_path: Path to the JSON file.
    :return: JSON object containing the contents of the JSON file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("File not found: %s", file_path)
    except json.JSONDecodeError:
        logging.error("File is not a valid JSON file: %s", file_path)
    return None

def write_to_json(output_data: dict[str, str], output_path: Path):
    """
    Writes data to a JSON file.
    
    :param output_data (dict): Data to be written to the file.
    :param output_path (Path): Path to the output JSON file.
    """
    with open(Path(output_path), 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
    logging.info("Data written to %s", output_path)


if __name__ == '__main__':
   typer.run(label)