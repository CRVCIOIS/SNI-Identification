import json
import logging
from pathlib import Path
from scripts.extract import DataExtractor
import typer
import tldextract
from typing_extensions import Annotated



def extract_wrapper(
    input_path_dataset: Annotated[Path, typer.Argument(
            exists=True, 
            file_okay=True, 
            dir_okay=False, 
            readable=True, 
            resolve_path=True, 
            formats=["json"], 
            help="The path to the input dataset file."
            )], 
    input_path_scraped: Annotated[Path, typer.Argument(
            exists=True, 
            file_okay=True, 
            dir_okay=False, 
            readable=True, 
            resolve_path=True, 
            formats=["json"], 
            help="The path to the input scraped data file."
            )], 
    output_path: Annotated[Path, typer.Argument(
            exists=False, 
            file_okay=True, 
            dir_okay=False, 
            resolve_path=True, 
            formats=["json"], 
            help="The path to the output data file."
            )],
    extract_meta: Annotated[bool, typer.Argument()],
    extract_body: Annotated[bool, typer.Argument()],
    p_only: Annotated[bool, typer.Argument()]):
    """
    Wrapper for the extract class. Extracts text from raw HTML in the scraped data
    and inserts it into the dataset.

    :param input_path_dataset (Path): Path to the dataset input file.
    :param input_path_scraped (Path): Path to the scraped data input file.
    :param output_path (Path): Path to the output file.
    :param extract_meta (bool): Argument for extracting meta.
    :param extract_body (bool): Argument for extracting body.
    :param p_only (bool): Argument for extracting only paragraphs.
    """
    dataset = open_json(input_path_dataset)
    scraped_data = open_json(input_path_scraped)

    if (dataset is not None) and (scraped_data is not None):
        extractor = DataExtractor()
        domain_text = {}  # Dictionary to store extracted text: {domain: text}
        
        for scraped_item in scraped_data:
            extractor.create_soup_from_string(scraped_item['raw_html'])
            extracted_text = extractor.extract(p_only=p_only, extract_body=extract_body, extract_meta=extract_meta)
            domain_text[scraped_item['domain']] = f'{domain_text.get(scraped_item["domain"], "")} {extracted_text}'
        
        for data_point in dataset:
            domain = f'{tldextract.extract(data_point["url"]).domain}.{tldextract.extract(data_point["url"]).suffix}'
            if domain in domain_text:
                data_point['text'] = domain_text[domain]

        write_to_json(dataset, output_path)


def open_json(file_path):
    """
    Opens the specified file and returns its contents as a JSON object.

    :param file_path (Path): Path to the file.
    :returns: The contents of the file as a JSON object, 
        or None if the file cannot be opened or is not a valid JSON file.
    """
    try:
        with open(Path(file_path), 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("File not found: %s", file_path)
    except json.JSONDecodeError:
        logging.error("File is not a valid JSON file: %s", file_path)
    return None


def write_to_json(output: list, output_path: Path):
    """
    Writes the output data to a JSON file.

    :param output (list): The data to be written.
    :param output_path (Path): Path to the output file.
    """
    with open(Path(output_path), 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    logging.info("Data written to %s", output_path)


if __name__ == '__main__':
    typer.run(extract_wrapper)