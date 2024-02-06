import json
import logging
from pathlib import Path
from extract import DataExtractor
import typer


def open_file(file_path):
    """
    Opens a file and loads the data into a dictionary.
    :param file_path: path to the file with the scraped data.
    :return: loaded data as a dictionary or None if file not found or not a valid JSON file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("File not found: %s", file_path)
    except json.JSONDecodeError:
        logging.error("File is not a valid JSON file: %s", file_path)
    return None


def write_to_file(restructured_json, output_directory, output_file_name=None):
    """
    Writes the restructured data to a file.
    :param restructured_json: restructured data
    :param output_directory: path to the directory where the restructured data will be saved.
    :param output_file_name: name of the output file (optional)
    """
    Path(output_directory).mkdir(parents=True, exist_ok=True)
    file_name = output_file_name or Path(file_path).name
    with open(f'{output_directory}/{file_name}.json', 'w', encoding='utf-8') as jsonfile:
        json.dump(restructured_json, jsonfile, indent=4, ensure_ascii=False)
    logging.info("Data written to %s", output_directory)


def postprocess(
    file_path: Path = typer.Argument(..., exists=True, dir_okay=False), 
    output_directory: Path = typer.Argument(..., dir_okay=True), 
    output_file_name: str  = typer.Argument()):
    """
    Postprocesses the scraped data into desired structure.
    :param file_path: path to the file with the scraped data.
    :param output_directory: path to the directory where the restructured data will be saved.
    :param output_file_name: name of the output file (optional)
    """
    input_data = open_file(file_path)
    if input_data is not None:
        restructured_json = []
        extractor = DataExtractor()
        for item in input_data:
            for existing_item in restructured_json:
                # If domain exists, append 'url' and 'raw_html' to
                # the text
                if existing_item['domain'] == item['domain']:
                    extractor.create_soup_from_string(item['raw_html'])
                    existing_item['text'] = f'{existing_item["text"]} {extractor.extract(p_only=True)}'
                    break
            # If the domain is not in restructured_json, add item to new
            # domain
            else:
                extractor.create_soup_from_string(item['raw_html'])
                new_item = {
                    "domain": item['domain'],
                    "SNI": "",
                    "text": extractor.extract(p_only=True),
                }
                restructured_json.append(new_item)
        write_to_file(restructured_json, output_directory, output_file_name)


if __name__ == '__main__':
    typer.run(postprocess)