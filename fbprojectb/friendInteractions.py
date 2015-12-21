import pymongo
from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client['FB_NoUse']
collection = db['interactions']
db2 = client['fbapp-DB']
collection2 = db2['fb-users']
collection3 = db2['fb-interactions']
user = collection2.find()[1]['name']
interactions = collection.find_one({'nodeA':user,'nodeB':"Kavita"})
print interactions
