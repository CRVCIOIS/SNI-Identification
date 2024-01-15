
from pathlib import Path

import spacy
import srsly
import typer
from spacy.pipeline.tok2vec import DEFAULT_TOK2VEC_MODEL
from spacy.tokens import DocBin


def main(
        input_path: Path = typer.Argument(..., exists=True, dir_okay=False),
        output_path: Path = typer.Argument(..., dir_okay=False),
):
    nlp = spacy.blank("sv")
    config = {"model": DEFAULT_TOK2VEC_MODEL}
    nlp.add_pipe("tok2vec", config=config)
    doc_bin = DocBin()
    records = srsly.read_json(input_path)
    for record in records:
        doc = nlp.make_doc(record["text"])
        # cats = {"Growing of rice": 1}
        doc.cats[record["sni"]] = 1
        doc_bin.add(doc)    
    out_file = output_path 
    doc_bin.to_disk(out_file)

if __name__ == "__main__":
    typer.run(main)

