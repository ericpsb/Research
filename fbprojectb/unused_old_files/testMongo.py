import pymongo
from pymongo import MongoClient


client = MongoClient('localhost', 27017)
#db = client['fb_nonuse_Sep_15']

#collection = db['interactions']
db2 = client['fbapp-DB']
collection2 = db2['fb-users']
collection3 = db2['fb-interactions']
#print db.collection_names()
#events = db['user']
#for doc in events.find():
#  print doc
#or doc in collection.find({'nodeA':'Ritu Shinde'}):
  #   print doc
#print collection.find_one({'large_name':'Yihui Fu','small_name':'Xiong Chu'})
#for doc in Yihui:
 #   print doc
#nodes = Yihui['nodes']
#links = Yihui['links']
#json = {'nodes':nodes,'links':links}
#print collection.find_one({'large_name': 'Yihui Fu','small_name': 'Jessica Putri'})
#print collection2.find_one({"name":"Eric Baumer"})['user id']
#collection.update({'author':"Mike"},{"$set":{'age':50}})
#collection.update(collection.find()[2],{"$unset":{'json':""}})
#collection.update({'user id':"10205816450603289"},{"$unset":{'json':""}})
#for doc in collection2.find():
#    print doc["name"]
#    print doc["user id"]
collection2.delete_one({"name":"Yihui Fu"})
#for doc in  collection2.find():
#     print doc
 #    collection2.update(doc,{"$unset":{'json':""}})
#     print doc 
#for doc in collection3.find():
 #    collection3.delete_one(doc)
 #    print doc

#cursor = collection2.find().batch_size(1)
#print cursor[0]

#collection2.update(Yihui,{"$set":{'name':Yihui['first_name']+" "+Yihui['last_name']}})
#collection2.delete_one({'name':"Neha Deshmukh"})
#for doc in collection2.find():
 #    print doc



#print collection2.find()[2]
#for key in Yihui.keys():
 #  if ("id" in key):
  #     print key+":"+str(Yihui[key])

#for post in collection.find():
# print post


#collection.update(Yihui,{"$unset":{"json":""}})
#print type(Yihui['json'])
