#!/usr/bin/env python
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
import sys
import simplejson

def main():
#Get user from Database
  i = ""
  try:
     i = json.loads(sys.argv[1])
  except :
     print "ERROR"
     sys.exit(1)
  client = MongoClient('localhost', 27017)
  db2 = client['fbapp-DB']
  collection2 = db2['fb-users']
  collection3 = db2['fb-interactions']
  admin_token = ""
  user = collection2.find_one({"user id":str(i)})   
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
  fb_feed = "https://graph.facebook.com/v2.9/me?fields=feed&access_token="+access_token
  data = requests.get(fb_feed).json()
  if 'feed' in data:
          first_interaction = data['feed']['data'][0]
          story1 = first_interaction['story']
          story2 = "" 
          date1 = dateparser.parse(first_interaction['created_time']).strftime('%m/%d/%y')
          date2 = ""
          x = data["feed"]
          while "next" in x["paging"]: 
            url = x["paging"]["next"]
            data = requests.get(url).json()
            if "data" in data:
               if data["data"] == [] : 
                   break 
               last_interaction = data['data'][-1] 
               if "story" in last_interaction:
                   story2 = last_interaction['story']
               elif "message" in last_interaction:
                   story2 = last_interaction["message"]
               date2 = dateparser.parse(last_interaction['created_time']).strftime('%m/%d/%y')
            x = data
          fb_events = "https://graph.facebook.com/v2.9/me?fields=events&access_token="+access_token
          events_data = requests.get(fb_events).json()
          no_of_events = len(events_data['events']['data'])
          while "next" in events_data:
               url = events_data["next"]
               events_data = requests.get(url).json()
               if "data" in events_data:
                  no_of_events += len(events_data['events']["data"])
          friends = "https://graph.facebook.com/v2.9/me?fields=friends&access_token="+access_token
          friendsData = requests.get(friends).json()
          friends_count = friendsData["friends"]["summary"]["total_count"]  
          jsonTemp = {}
          jsonTemp['first'] = [story1,date1]
          jsonTemp['last'] = [story2,date2]
          jsonTemp['events'] = no_of_events
          jsonTemp["friends"] = friends_count
          collection2.update(user,{"$set":{'jsonTemp':jsonTemp}})
          collection2.update(user,{"$set":{'vizDone':0}}) 
          return jsonTemp
          
if __name__ == "__main__":
       js  = main()
       data = json.dumps(js)
       print data 
