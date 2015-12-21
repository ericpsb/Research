from newViz import *
import facebook
import facepy
import requests
import urllib2
import json
from apscheduler.scheduler import Scheduler
import pymongo
from pymongo import MongoClient
import time
#fixing the Insecure platform issue
import urllib3.contrib.pyopenssl
import dateutil.parser as dateparser
import gridfs
from facepy.exceptions import OAuthError
from facepy.exceptions import FacebookError
from itertools import combinations
import itertools
import logging

def sideViz(id_list):
#Get user from Database
  client = MongoClient('localhost', 27017)
  db1 = client['fb_nonuse_Nov_20']
  collection1 = db1['interactions']
  db2 = client['fbapp-DB']
  collection2 = db2['fb-users']
  collection3 = db2['fb-interactions']
  admin_token = ""
  for uid in id_list:
      #user = collection2.find()[1]
     user = collection2.find_one({"id":uid})
     
     if user == None:
     	continue

     print user
     if ('json' in user):  
	 name = user['name']
	 Id = user['user id']
	 access_token = user['access_token']
	 graph = facepy.GraphAPI(access_token)
	 admin = facepy.GraphAPI(admin_token)
	 nodes = []
	 friends = []
	 links =[]
	 # get profile object
	 user_name = graph.get('me')['name']
	 nodes.append({'name':user_name})
	 linkIndex = 0
	 nodeIndex = 1
	 cursor1 = collection1.find({"large_id":Id})
	 cursor1.batch_size(30)
	 if (cursor1 != None):
	   for doc in cursor1:
	    interactions = {}
	    interactions["source"] = user_name
	    message = []
	    nodes.append({'name':doc['small_name']})
	    interactions['target']=doc['small_name']
	    createJson(user_name,doc,graph,interactions,message,nodes,links,linkIndex,admin,access_token)
	    linkIndex += 1
	    collection3.insert_one(interactions)
	 cursor3 = collection1.find({"small_id":Id})
	 cursor3.batch_size(30)
	 if (cursor3 != None):
	  for doc in cursor3:
	    interactions = {}
	    interactions["source"] = user_name
	    message = []
	    nodes.append({'name':doc['large_name']})
	    interactions['target']=doc['large_name']
	    createJson(user_name,doc,graph,interactions,message,nodes,links,linkIndex,admin,access_token)
	    linkIndex += 1
	    collection3.insert_one(interactions)


	 cursor2 = collection1.find({"collected_from":{ "$in": [{'name':name,'id':Id}] }})
	 cursor2.batch_size(30);
	 for doc in cursor2:
	   if (doc["large_id"] != Id and doc["small_id"] != Id):
	    if ({'name':doc['large_name']} not in nodes):
	        interactions = {}
	        nodes.append({'name':doc['large_name']})
	        interactions['source']=user_name
	        interactions['target']=doc['large_name']
	        try:
	           collection3.insert_one(interactions)
	        except:
	           print "Interactions exists:"+doc['large_name']

	    if ({'name':doc['small_name']} not in nodes):
	        interactions = {}
	        nodes.append({'name':doc['small_name']})
	        interactions['source']=user_name
	        interactions['target']=doc['small_name']
	        try:
	           collection3.insert_one(interactions)
	        except:
	           print "interaction exists:"+doc['small_name']

	    interactions = {}
	    interactions['source'] = doc["large_name"]
	    message = []
	    interactions['target'] = doc["small_name"]

	    #if (collection3.find_one({"source":doc["large_name"],"target":doc["small_name"]}) != None):
	          # collection3.delete_one(collection3.find_one({"source":doc["large_name"],"target":doc["small_name"]}))
	    #if (collection3.find_one({"source":doc["small_name"],"target":doc["large_name"]}) != None):
	         # collection3.delete_one(collection3.find_one({"source":doc["small_name"],"target":doc["large_name"]}))

	    if (doc != {} and doc != None):
	        createJson(user_name,doc,graph,interactions,message,nodes,links,linkIndex,admin,access_token)
	    linkIndex += 1

	    collection3.insert_one(interactions)

	 print "Done"
	 jsons = {'nodes':nodes,'links':links}
	 try :
	    collection2.update(user,{"$set":{'json':jsons}})
	    lol = 2
	 except :
	    lol = 1

         logging.info("Updated {}\'s visualization".format(uid))
