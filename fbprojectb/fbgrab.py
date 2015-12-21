#!/usr/bin/env python
#do all imports here
import facebook
import facepy 
import urllib2
import json
from apscheduler.scheduler import Scheduler
import pymongo 
from pymongo import MongoClient
import time
#fixing the Insecure platform issue
import urllib3.contrib.pyopenssl



#build graph object
#graph = facebook.GraphAPI(access_token='CAAWfa2M5ZBkEBAB28vh6gC2W4kryVIZCgwG6EIgUkPai09yiRH88tBgH0E7tscfxlbuH3O7wEuT7trcORAzqVs6Es3JmBG440lSYweTfhjirM9iHFXI7T66zaeazaZC3J9ZBGLWp10WoLae70jnwYiQS1IDjSH1xHWWW191ubRy9ErBZBqGm9Ga2BUOOMJu9X5GVDGx5xvQ1vBvkFnQ9KnFilWH4EtjYZD')

#get profile object
#profile = graph.get_object("me")

#get friends information
#friends = graph.get_connections("me", "friends")

#print friends information
#print friends

#test print here
#print "yo!"
#graph = facepy.GraphAPI('CAAWfa2M5ZBkEBAGnSJ2obY5O3x3Tn4sCXPtHQgJiQBtKgU4HMXKXVN9tO4vE0jGZCr2zGccVl2Lx5YbQbiNhgFCnZCGWZBkA8qXLBBxhNmPAn4KLfqAaj8zJ9bksSXvndZCsY5rg7ZCWriDQvar7UxPA18bFLSaeGAxfPBfH5rdby2yzAkEmhi')
#profile =graph.get('me')

client = MongoClient('localhost', 27017)
#db = client['fbapp-DB']
#collection = db['fb-users']
db = client['test-database']
collection = db['test-collection']

def main():
    post = {"author":"Harry"}
    collection.insert_one(post)

if __name__=='__main__': 
    main()
