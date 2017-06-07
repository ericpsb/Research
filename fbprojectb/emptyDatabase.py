from pymongo import MongoClient
import config

client = MongoClient(config.get_connection_string())
db = client['fbapp-DB_test_5_17_17']
collections = db.collection_names()

for name in collections:
    result = db[name].delete_many({})

db = client['fb_nonuse_test_5_17_17']
collections = db.collection_names()

for name in collections:
    result = db[name].delete_many({})
