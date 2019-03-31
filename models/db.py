# coding: utf-8


import os
import json
import bson
from bson import ObjectId
from pymongo import MongoClient

config_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
config_path = os.path.join(config_path, 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)


class DB:

    mongo_uri = config['mongo_uri']
    client = MongoClient(mongo_uri)
    db = client[config['db']]

    @classmethod
    def convert_objectid(cls, query):
        if '_id' in query and not isinstance(query['_id'], ObjectId):
            # convert to objectid
            try:
                query['_id'] = ObjectId(query['_id'])
            except bson.errors.InvalidId as e:
                raise e

    @classmethod
    def find_all(cls, collection_name):
        results = DB.db[collection_name].find()
        return results

    @classmethod
    def find_one(cls, collection_name, query, custom_id=False):
        if not custom_id:
            DB.convert_objectid(query)
        result = DB.db[collection_name].find_one(query)
        if result:
            result.pop('_id')
        return result

    @classmethod
    def create_one(cls, collection_name, document):
        object_id = DB.db[collection_name].insert_one(document).inserted_id
        # TODO: check if success
        # remove object id
        document.pop('_id')
        return str(object_id)

    @classmethod
    def update_one(cls, collection_name, query, document, custom_id=False):
        if not custom_id:
            DB.convert_objectid(query)
        result = DB.db[collection_name].\
            update_one(query, {'$set': document}, upsert=True)
        return result.modified_count == 1

    @classmethod
    def delete_one(cls, collection_name, query, custom_id=False):
        if not custom_id:
            DB.convert_objectid(query)
        result = DB.db[collection_name].delete_one(query)
        return result.deleted_count == 1

