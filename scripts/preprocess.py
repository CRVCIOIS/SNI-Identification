"""
    This script preprocesses the input data and saves the processed labeled documents in binary form to the output path.

    The main function takes two arguments:
    - input_path (Path): Path to the input data file.
    - output_path (Path): Path to save the processed documents.

    The script uses the spacy library to process the text data. It reads the input data from a JSON file, where each record contains a "text" field and a "sni" field representing the text and the label respectively. It then tokenizes the text using a blank Swedish language model from spacy, assigns the label to the document, and adds it to a DocBin object. Finally, the DocBin object is saved to the output path in binary format.

    Example usage:
    python preprocess.py input.json output.spacy
"""

from pathlib import Path
import spacy
import srsly
import typer
from spacy.tokens import DocBin
from copy import copy

def main(
        input_path: Path = typer.Argument(..., exists=True, dir_okay=False),
        output_path: Path = typer.Argument(..., dir_okay=False),
):
    """
    Preprocesses the input data and saves the processed labeled documents in binary form to the output path.
    :param input_path (Path): Path to the input data file.
    :param output_path (Path): Path to save the processed documents.
    """
    
    nlp = spacy.blank("sv")
    doc_bin = DocBin()
    records = srsly.read_json(input_path)
    labels = {}
    for record in records:
        if labels.get(record["SNI"]) is None:
            labels[record["SNI"]] = 0
        
    for record in records:
        doc_label = copy(labels)
        doc_label[record["SNI"]] = 1
        doc = nlp.make_doc(record["text"])
        doc.cats = doc_label
        doc_bin.add(doc)
    
    doc_bin.to_disk(output_path)
if __name__ == "__main__":
    typer.run(main)