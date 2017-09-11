from pymongo import MongoClient
import config

client = MongoClient(config.get_connection_string())
db = client['fbapp-DB_test']
collections = db.collection_names()

for name in collections:
    if name == 'system.indexes':
        continue
    # result = db[name].delete_many({})
    result = db[name].drop()

db = client['fb_nonuse_test']
collections = db.collection_names()

for name in collections:
    if name == 'system.indexes':
        continue
    # result = db[name].delete_many({})
    result = db[name].drop()
