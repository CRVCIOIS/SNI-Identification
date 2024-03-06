import pytest
from pathlib import Path
import json
from pipeline.divide_dataset import main
DATASET = [
            {
                "company_name": "SSAB",
                "SNI": "123456789",
                "text": "Lorem Lipsum",
                "phone_number": "123456789",
                "org_number": "123456789",
                "address": "123456789",
                "municipality": "Stockgolm",
                "postal_code": "123456789",
                "url": "https://ssab.se/"
            },
            {
                "company_name": "LKAB",
                "SNI": "123456789",
                "text": "Lorem Lipsum",
                "phone_number": "123456789",
                "org_number": "123456789",
                "address": "123456789",
                "municipality": "Stockgolm",
                "postal_code": "123456789",
                "url": "https://lkab.com/"
            }
        ]

@pytest.fixture
def temp_dataset(tmp_path):
    """
    Create a temporary input file 
    The file has the same structure as the dataset.
    """
    input_file = tmp_path / "input_data.json"
    with open(Path(input_file), 'w', encoding='utf-8') as f:
        json.dump(DATASET, f, indent=4, ensure_ascii=False)
        return input_file
    
def test_main(temp_dataset, tmp_path):
    temp_output = tmp_path / "output_data.json"

    main(temp_dataset, temp_output, 1)

    with open(temp_dataset, 'r') as f:
        data1 = json.load(f)

    with open(temp_output, 'r') as f:
        data2 = json.load(f)
    
    data1_true = [DATASET[0]]
    data2_true = [DATASET[1]]

    assert data1 == data1_true
    assert data2 == data2_true

