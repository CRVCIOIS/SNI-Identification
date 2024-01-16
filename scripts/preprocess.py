
from pathlib import Path

import spacy
import srsly
import typer
from spacy.tokens import DocBin


def main(
        input_path: Path = typer.Argument(..., exists=True, dir_okay=False),
        output_path: Path = typer.Argument(..., dir_okay=False),
):
    """
    Preprocesses the input data and saves the processed labeld documents in binary form to the output path.

    Args:
        input_path (Path): Path to the input data file.
        output_path (Path): Path to save the processed documents.

    Returns:
        None
    """
    nlp = spacy.blank("sv")
    doc_bin = DocBin()
    records = srsly.read_json(input_path)
    for record in records:
        doc = nlp.make_doc(record["text"])
        doc.cats[record["sni"]] = 1
        doc_bin.add(doc)    
    doc_bin.to_disk(output_path)

if __name__ == "__main__":
    typer.run(main)

