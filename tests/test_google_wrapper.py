import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from google_wrapper import main

@patch('google_wrapper.GoogleSearchAPI')
def test_main(mock_google_search_api):
    # Arrange
    mock_google_search_api.return_value.search.return_value = 'http://example.com'
    input_path = Path('input.json')
    output_path = Path('output.json')
    input_data = [
        {"name": "Test Company", "url": ""},
        {"name": "", "url": "http://example.com"},
        {"name": "Another Test Company", "url": ""}
    ]
    expected_output_data = [
        {"name": "Test Company", "url": "http://example.com"},
        {"name": "", "url": "http://example.com"},
        {"name": "Another Test Company", "url": "http://example.com"}
    ]

    with open(input_path, 'w') as f:
        json.dump(input_data, f)

    # Act
    main(input_path, output_path)

    # Assert
    with open(output_path, 'r') as f:
        output_data = json.load(f)

    assert output_data == expected_output_data

    # Cleanup
    input_path.unlink()
    output_path.unlink()