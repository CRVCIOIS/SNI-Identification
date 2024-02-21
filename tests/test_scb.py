import os
import json
from unittest.mock import patch, MagicMock, create_autospec, mock_open
import pytest
from scripts.scb import *
from scripts.scb_wrapper import SCBapi
from scripts.mongo import get_client
from definitions import ROOT_DIR

@pytest.fixture
def sni_filter():
    return [
        {
            'VardeLista': [
                {'Varde': '01', 'Text': 'Code 01'},
                {'Varde': '03', 'Text': 'Code 03'}
            ]
        }
    ]

@pytest.fixture
def sni_response():
    return [
        {},
        {
            'VardeLista': [
                {'Varde': '01', 'Text': 'Code 01'},
                {'Varde': '02', 'Text': 'Code 02'},
                {'Varde': '03', 'Text': 'Code 03'}
            ]
        }
    ]

@pytest.fixture
def sni_db_response():
    return [
        {'sni_code': '01', 'description': 'Code 01'},
        {'sni_code': '02', 'description': 'Code 02'},
        {'sni_code': '03', 'description': 'Code 03'}
    ]
    
@pytest.fixture
def sni_db_result():
    return [
        {'sni_code': '01', 'description': 'Code 01'},
        {'sni_code': '02', 'description': 'Code 02'},
        {'sni_code': '03', 'description': 'Code 03'}
    ]

@patch('builtins.open', new_callable=mock_open)
@patch('scripts.scb.SCBapi')
@patch('scripts.scb.get_client')
def test_store_codes(mock_get_client, mock_scb_api, mock_file, sni_filter, sni_response):
    
    # Mock the response from the scb api get request
    mock_scb_api.return_value.get.return_value.json.return_value = sni_response

    # Mock the contents of the filtered_sni.json file
    mock_file.return_value.read.return_value = json.dumps(sni_filter)
    
    store_codes()
    
    
    mock_file.assert_called_once_with(os.path.join(ROOT_DIR,'assets','filtered_sni.json'), 'r', encoding='utf-8')
    mock_get_client.return_value[DB][SNI].insert_many.assert_called_once_with([
        {'sni_code': '01', 'description': 'Code 01'},
        {'sni_code': '03', 'description': 'Code 03'}
    ])
    mock_get_client.return_value[DB][SNI].create_index.assert_called_once_with('sni_code')

@patch('scripts.scb.get_client')
def test_fetch_codes(mock_get_client, mock_sni_db_response, sni_db_result):
    
    mock_get_client.return_value[DB][SNI].find.return_value = mock_sni_db_response
    
    result = fetch_codes()
    
    assert mock_get_client.return_value[DB][SNI].find.called
    assert result == sni_db_result



@patch('scripts.scb.SCBapi')
@patch('scripts.scb.get_client')
def test_store_municipalities(mock_get_client, mock_scb_api, mun_response):
    pass