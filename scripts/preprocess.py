"""
    This script preprocesses the input data and saves the processed labeled documents in binary form to the output path.

    The main function takes two arguments:
    - input_path (Path): Path to the input data file.
    - output_path (Path): Path to save the processed documents.

    The script uses the spacy library to process the text data. It reads the input data from a JSON file, where each record contains a "text" field and a "sni" field representing the text and the label respectively. It then tokenizes the text using a blank Swedish language model from spacy, assigns the label to the document, and adds it to a DocBin object. Finally, the DocBin object is saved to the output path in binary format.

    Example usage:
    python preprocess.py input.json output.spacy
"""
from copy import copy
from pathlib import Path

import spacy
import typer
from spacy.language import Language
from spacy.tokens import DocBin

from scripts.scb import SCBinterface


def create_doc_for_company(labels: dict, company: dict, nlp: Language, multi_label=False):
    """
    Create a spacy Doc object with the given labels and company data.
    :param labels (dict): Dictionary of labels.
    :param company (dict): Company to process.
    :param nlp (spacy.Language): Language model to use for processing.
    :param multi_label (bool): Whether to use multi-label classification.
    :return (spacy.Doc): Processed Doc object.
    """
    text = str()
    
    """
    Concatenate all data points (data per url) into one document per company
    """
    for data_point in company["data"]:
        text = text + " " + data_point["data"]
    
    if len(text) >= 1000000:
        text = text[:1000000]
    
    doc = nlp.make_doc(text)
    
    if multi_label:
        for company_code in company["branch_codes"]:
                labels[company_code] = 1
        doc.cats = labels
    else:
        labels[company["branch_codes"][0]] = 1
        doc.cats = labels
    return doc

def main(
        output_train_path: Path = typer.Argument(..., dir_okay=False),
        output_dev_path: Path = typer.Argument(..., dir_okay=False),
):
    """
    Preprocesses the input data and saves the processed labeled documents in binary form to the output path.
    :param output_path (Path): Path to save the processed documents.
    """
    
    nlp = spacy.blank("sv")
    nlp.max_length = 20000000
    doc_train = DocBin()
    doc_eval = DocBin()
    
    scb = SCBinterface()
    
    codes = {}
    for code in scb.fetch_codes():
        codes[code] = 0
        
    for company in scb.fetch_train_set():
        labels = copy(codes) # Copy needed to avoid reference to same dictionary
        doc = create_doc_for_company(labels, company, nlp, multi_label=False)
        doc_train.add(doc)
            
    for company in scb.fetch_dev_set():
        labels = copy(codes) # Copy needed to avoid reference to same dictionary
        doc = create_doc_for_company(labels, company, nlp, multi_label=False)
        doc_eval.add(doc)

    doc_train.to_disk(output_train_path)
    doc_eval.to_disk(output_dev_path)
if __name__ == "__main__":
    typer.run(main)