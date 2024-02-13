import json
import logging
from pathlib import Path
from extract import DataExtractor
import typer


def postprocess(
    input_path: Path = typer.Argument(..., exists=True, dir_okay=False), 
    output_path: Path = typer.Argument(..., exists=False, dir_okay=False),
    extract_meta: bool  = typer.Argument(),
    extract_body: bool  = typer.Argument(),
    p_only: bool  = typer.Argument()):
    """
    Postprocesses the input data into desired structure, extracting relevant information from HTML and writing it to a file.

    :param input_path (Path): Path to the input file.
    :param output_file_name (Path): Path of the output file.
    :param extract_meta (bool): Argument for extracting meta.
    :param extract_body (bool): Argument for extracting body.
    :param p_only (bool): Argument for extracting only paragraphs.
    """
    input_data = open_file(input_path)
    if input_data is not None:
        output_data = []
        extractor = DataExtractor()
        
        for input_item in input_data:
            for output_item in output_data:
                if output_item['domain'] == input_item['domain']:
                    extractor.create_soup_from_string(input_item['raw_html'])
                    output_item['text'] = f'{output_item["text"]} {extractor.extract(p_only=p_only, extract_body=extract_body, extract_meta=extract_meta)}'
                    break
            else:
                extractor.create_soup_from_string(input_item['raw_html'])
                new_item = {
                    "domain": input_item['domain'],
                    "SNI": "",
                    "text": extractor.extract(p_only=p_only, extract_body=extract_body, extract_meta=extract_meta),
                }
                output_data.append(new_item)
        write_to_file(output_data, output_path)


def open_file(file_path):
    """
    Opens the specified file and returns its contents as a JSON object.

    :param file_path (Path): Path to the file.
    :returns: The contents of the file as a JSON object, or None if the file cannot be opened or is not a valid JSON file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error("File not found: %s", file_path)
    except json.JSONDecodeError:
        logging.error("File is not a valid JSON file: %s", file_path)
    return None


def write_to_file(output, output_path):
    """
    Writes the output data to a JSON file.

    :param output: The data to be written.
    :param output_path (Path): Path to the output file.
    """
    with open(Path(f'{output_path}.json'), 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
    logging.info("Data written to %s", output_path)


if __name__ == '__main__':
    typer.run(postprocess)