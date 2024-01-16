from pathlib import Path

import pytest
import spacy
from spacy.tokens import DocBin

from scripts.preprocess import main


@pytest.fixture
def input_path(tmp_path):
    # Create a temporary input file
    input_file = tmp_path / "input.json"
    input_file.write_text('[{"text": "example text", "sni": "example_label"}]')
    return input_file

@pytest.fixture
def output_path(tmp_path):
    # Create a temporary output directory
    return tmp_path / "output"/"test.spac"

def test_main(input_path, output_path):
    # Call the main function with the test input and output paths
    main(input_path, output_path)

    # Check if the output directory exists
    assert output_path.exists()

    # Load the saved documents from the output directory
    doc_bin = DocBin().from_disk(output_path)
    nlp = spacy.blank("sv")
    # Check if the document was processed and saved correctly
    assert len(doc_bin) == 1
    for doc in doc_bin.get_docs(nlp.vocab):
        assert doc.text == "example text"
        assert doc.cats["example_label"] == 1
    # assert doc_bin.strings[0] == "example"
    # assert doc_bin.strings[1] == "text"
    # assert doc.text == "example text"
    # assert doc.cats["example_label"] == 1

    # Clean up the temporary files
    input_path.unlink()
    
    # Remove the temporary output directory
    output_path.rmdir()
    
# Run the test with pytest
# $ pytest scripts/test_preprocess.py
