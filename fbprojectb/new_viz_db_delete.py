from pymongo import MongoClient
import config

client = MongoClient(config.get_connection_string())

# db = client['newVizTest']
# result = db['app_interactions'].delete_many({})
# result = db['users'].update_one({}, {'$unset': {'json': 1}})

db = client['fbapp-DB_test']
result = db['fb-interactions'].delete_many({})
result = db['fb-users'].update_one({}, {'$unset': {'json': 1}})
