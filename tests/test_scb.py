"""
Tests for SCB interface.
"""
import pytest
from scripts.scb import *
from scripts.scb_wrapper import SCBapi
from pymongo import MongoClient

@pytest.fixture
def scb_interface():
    """
    Fixture for SCB interface.
    """
    return SCBinterface()

def test_init(scb_interface):
    """
    Test if the correct clients are generated. 
    """
    assert type(scb_interface.scb_api) is SCBapi
    assert type(scb_interface.client) is MongoClient
