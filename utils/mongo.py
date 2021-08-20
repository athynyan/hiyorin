import os
from pymongo import MongoClient


def connect_to_mongo():
    mongo_client = MongoClient(os.getenv('MONGO_URL'))
    return mongo_client[os.getenv('MONGO_DB_NAME')]


def get_mongo_collection(collection):
    return connect_to_mongo()[collection]


def get_document(key, value, collection):
    collection = get_mongo_collection(collection)
    return collection.find_one({key: value})


def add_document(doc, collection):
    collection = get_mongo_collection(collection)
    collection.insert_one(doc)


def update_document(doc, collection):
    pass


def remove_document(key, value, collection):
    collection = get_mongo_collection(collection)
    if collection.find_one({key: value}):
        collection.delete_one({key: value})
