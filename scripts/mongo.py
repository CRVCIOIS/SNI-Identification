"""
Methods for abstracting communication with Mongodb
"""
import os
from enum import StrEnum
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv
from definitions import ROOT_DIR
import bson

BACKUP_PATH = os.path.join(ROOT_DIR, "backup")
load_dotenv(os.path.join(ROOT_DIR, '.env'), override=True)

class Schema(StrEnum):
    """
    Used to loosely enforce a schema for MongoDB.
        Defines database name and collection names. 
    """
    # Database
    DB              = "SCB"
    # Collections
    SNI             = "SNI_codes"
    COMPANIES       = "companies"
    MUNICIPALITIES  = "municipalities"
    API_COUNT       = "api_count"
    LEGAL_FORMS     = "legal_forms"
    SCRAPED_DATA    = "scraped_data"
    EXTRACTED_DATA  = "extracted_data"
    METHODS         = "methods"
    DEV_SET         = "dev_set"
    TRAIN_SET       = "train_set"

def get_client():
    """
    Creates a mongo client (based on the connection string env-var) and returns it.
    
    :returns: a MongoClient object.
    """
    mongo_connection = os.getenv("MONGO_CONNECTION")
    client = MongoClient(mongo_connection)
    return client

def dump(collections: list[str], client:MongoClient, db_name:str):
    """
    Dumps the collections from the database to the backup folder.
    
    params:
    collections: list of collections to dump
    client: MongoClient object
    db_name: name of the database
    """
    db = client[db_name]
    for coll in collections:
        Path(BACKUP_PATH).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(BACKUP_PATH, coll + ".json"), "wb+") as f:
            for doc in db[coll].find():
                f.write(bson.BSON.encode(doc))

def restore(client:MongoClient, db_name:str):
    """
    Restores the collections from the backup folder to the database.
    
    params:
    client: MongoClient object
    db_name: name of the database
    """
    db = client[db_name]
    for coll in os.listdir(BACKUP_PATH):
        with open(os.path.join(BACKUP_PATH, coll), "rb+") as f:
            db[coll.split('.')[0]].insert_many(bson.decode_all(f.read()))