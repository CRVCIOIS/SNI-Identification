"""
    This script preprocesses the input data and saves the processed labeled documents in binary form to the output path.

    The main function takes two arguments:
    - input_path (Path): Path to the input data file.
    - output_path (Path): Path to save the processed documents.

    The script uses the spacy library to process the text data. It reads the input data from a JSON file, where each record contains a "text" field and a "sni" field representing the text and the label respectively. It then tokenizes the text using a blank Swedish language model from spacy, assigns the label to the document, and adds it to a DocBin object. Finally, the DocBin object is saved to the output path in binary format.

    Example usage:
    python preprocess.py input.json output.spacy
"""
import logging
import spacy
import typer
from copy import copy
from pathlib import Path
from typing_extensions import Annotated
from spacy.language import Language
from spacy.tokens import DocBin
from adapters.train import TrainAdapter
from adapters.scb import SCBAdapter

def create_doc_for_company(labels: dict, company: dict, nlp: Language,  min_data_length: int):
    """
    Create a spacy Doc object with the given labels and company data.
    :param labels (dict): Dictionary of labels.
    :param company (dict): Company to process.
    :param nlp (spacy.Language): Language model to use for processing.
    :param min_data_length (int): Minimum length of data to include in the document.
    :return (spacy.Doc): Processed Doc object.
    """
    text = str()
    
    """
    Concatenate all data points (data per url) into one document per company
    """
    for data_point in company["data"]:
        text = text + " " + data_point["data"]
    
    if len(text) >= 1000000: # Spacy has a limit of 1000000 characters per document
        text = text[:1000000]
        logging.debug(f"Truncated company text to 1000000 characters")
    if len(text) < min_data_length:
        logging.debug(f"Skipping company with too short text length: {len(text)}")
        return None
    
    logging.debug("Processed company_id: %s, SNI: %s, document length: %s", company["company_id"], company['branch_codes'][0], len(text))
    doc = nlp.make_doc(text)
    labels_copy = copy(labels) # Copy needed to avoid reference to same dictionary
    labels_copy[company["branch_codes"][0]] = 1
    doc.cats = labels_copy
    return doc

def main(
        output_train_path: Annotated[Path, typer.Argument(...,dir_okay=False)],
        output_dev_path: Annotated[Path, typer.Argument(...,dir_okay=False)],
        output_test_path: Annotated[Path, typer.Argument(...,dir_okay=False)],
        min_data_length: Annotated[int, typer.Argument()] = 300
    ):
    """
    Preprocesses the input data and saves the processed labeled documents in binary form to the output path.
    :param output_path (Path): Path to save the processed documents.
    """
    
    nlp = spacy.blank("sv")
    nlp.max_length = 20000000
    doc_train = DocBin()
    doc_eval = DocBin()
    doc_test = DocBin()
    
    scb_adapter   = SCBAdapter()
    train_adapter = TrainAdapter()
    
    label_count = {"total_length": 0, "labels": {}}
    labels = {}
    for label in scb_adapter.fetch_codes():
        labels[label] = 0
        
    for company in train_adapter.fetch_train_set():
        doc = create_doc_for_company(labels, company, nlp, min_data_length)
        if doc is not None:
            doc_train.add(doc)
            label_count['labels'][company['branch_codes'][0]] = label_count['labels'].get(company['branch_codes'][0], 0) + 1
            label_count['total_length'] = label_count.get('total_length', 0) + len(doc.text)
            
    for company in train_adapter.fetch_dev_set():
        doc = create_doc_for_company(labels, company, nlp, min_data_length)
        if doc is not None:
            doc_eval.add(doc)
            label_count['labels'][company['branch_codes'][0]] = label_count['labels'].get(company['branch_codes'][0], 0) + 1
            label_count['total_length'] = label_count.get('total_length', 0) + len(doc.text)
    for company in train_adapter.fetch_test_set():
        doc = create_doc_for_company(labels, company, nlp, min_data_length)
        if doc is not None:
            doc_test.add(doc)
            label_count['labels'][company['branch_codes'][0]] = label_count['labels'].get(company['branch_codes'][0], 0) + 1
            label_count['total_length'] = label_count.get('total_length', 0) + len(doc.text)

    # Remove old files
    output_dev_path.unlink(missing_ok=True)
    output_train_path.unlink(missing_ok=True)
    output_test_path.unlink(missing_ok=True)
    logging.debug("Removed old corpus files")

    doc_train.to_disk(output_train_path)
    logging.info("Saved training data to %s", output_train_path)
    logging.info("Number of documents in training data: %s", len(doc_train))

    doc_eval.to_disk(output_dev_path)
    logging.info("Saved evaluation data to %s", output_dev_path)
    logging.info("Number of documents in evaluation data: %s", len(doc_eval))

    doc_eval.to_disk(output_test_path)
    logging.info("Saved test data to %s", output_test_path)
    logging.info("Number of documents in test data: %s", len(doc_test))
    
    logging.info("Preprocessing finished!")
    logging.info("Number of documents processed: %s", sum(label_count['labels'].values()))
    logging.info("Number of distinct labels processed: %s", len(label_count['labels']))
    logging.info("Number of documents per label:")
    for label in dict(sorted(label_count['labels'].items())):
        logging.info("Label %s: %s documents", label, label_count['labels'][label])

    logging.info("Total length of documents processed: %s", label_count['total_length'])
    logging.info("Average length of documents per label: %s", label_count['total_length']/len(label_count['labels']))

if __name__ == "__main__":
    from aux_functions.logger_config import conf_logger
    conf_logger(Path(__file__).stem)
    typer.run(main)