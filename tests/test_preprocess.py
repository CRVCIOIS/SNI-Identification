""" 
This file contains tests for the preprocess scripts. It uses the pytest library to run the tests.
To run simply execute the following command in the terminal:
> pytest scripts/test_preprocess.py
"""

import pytest
import spacy
from spacy.tokens import DocBin

from pipeline.preprocess import main


@pytest.fixture
def input_path(tmp_path):
    """
    Create a temporary input file and return its path.

    Args:
        tmp_path (str): The path to the temporary directory.

    Returns:
        str: The path to the created input file.
    """
    # Create a temporary input file
    input_file = tmp_path / "input.json"
    input_file.write_text('[{"text": "example text", "sni": "example_label"}]')
    return input_file

@pytest.fixture
def output_path(tmp_path):
    """
    Returns the path of a temporary output file.

    Args:
        tmp_path (str): The path of the temporary directory.

    Returns:
        str: The path of the temporary output file.
    """
    # Create a temporary output file
    return tmp_path / "test.spacy"

def test_main(input_path, output_path):
    """
    Test the main function by calling it with the test input and output paths.
    Check if the output directory exists and if the saved documents were processed and saved correctly.
    Clean up the temporary files after the test.
    
    Args:
        input_path (str): The path to the test input file.
        output_path (str): The path to the test output directory.
    """
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


    # Clean up the temporary files
    input_path.unlink()
    output_path.unlink()
    
