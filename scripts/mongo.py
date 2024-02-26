import os
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv
from definitions import ROOT_DIR
import bson

BACKUP_PATH = os.path.join(ROOT_DIR, "backup")
load_dotenv(os.path.join(ROOT_DIR, '.env'),verbose=True, override=True)

def get_client():
    mongo_host     = os.getenv("MONGO_HOST")
    mongo_auth_db  = os.getenv("MONGO_AUTH_DB", '')
    mongo_user     = os.getenv("MONGO_USER", '')
    mongo_pass     = os.getenv("MONGO_PASS", '')
    if (mongo_user == '') or (mongo_pass == ''):
        connection_string = f"mongodb://{mongo_host}"
    else:
        connection_string = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}{('/'+ mongo_auth_db) if mongo_auth_db !='' else ''}"
    client = MongoClient(connection_string)  
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
        Path().mkdir(parents=True, exist_ok=True)
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