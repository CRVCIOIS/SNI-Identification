"""
Tests for postprocess.
Input: List of dictionaries with the following keys: url, domain, raw_html.
Output: List of dictionaries with the following keys: domain, text.
It uses the pytest library to run the tests. To run simply execute the following command in the terminal:
> pytest tests/test_psotprocess.py
"""
from pathlib import Path
from scripts.label import label
import pytest
import json


@pytest.fixture
def temp_input_file(tmp_path):
    """

    """
    lst ={ 
        "ssab": { "SNI": "", "text": "text"}, 
        "lkab": { "SNI": "", "text": "text"},
        "bdx": { "SNI": "", "text": "text"}
        }

    input_file = tmp_path / "input.json"
    with open(Path(input_file), 'w', encoding='utf-8') as f:
        json.dump(lst, f, indent=4, ensure_ascii=False)
        return input_file
    
@pytest.fixture
def temp_sni_file(tmp_path):
    """
    """
    sni = {
        "ssab": "123",
        "lkab": "456",
        "bdx": "789"
        }
    
    input_file = tmp_path / "sni.json"
    with open(Path(input_file), 'w', encoding='utf-8') as f:
        json.dump(sni, f, indent=4, ensure_ascii=False)
        return input_file

def test_label(tmp_path, temp_input_file, temp_sni_file):
    """
    """
    temp_output_file = tmp_path / "output.json"
    label(temp_sni_file, temp_input_file, temp_output_file)
    
    with open(temp_output_file, 'r', encoding='utf-8') as f:
        labeled_data = json.load(f)
    
    assert labeled_data[0]["domain"] == "ssab" and labeled_data[0]["SNI"] == "123"
    assert labeled_data[1]["domain"] == "lkab" and labeled_data[1]["SNI"] == "456"
    assert labeled_data[2]["domain"] == "bdx" and labeled_data[2]["SNI"] == "789"
    
    
    temp_input_file.unlink() # delete the temp file
    temp_output_file.unlink() # delete the temp file
    
