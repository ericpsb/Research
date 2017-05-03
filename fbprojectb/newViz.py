#!/usr/bin/env python
#do all imports here
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

class GenerateViz():

    def init(self,userid):
          self.userid = userid
          client = MongoClient('localhost', 27017)
          db1 = client['fb_nonuse_Nov_20']
          collection1 = db1['interactions']
          db2 = client['fbapp-DB']
          collection2 = db2['fb-users']
          collection3 = db2['fb-interactions']
          admin_token = ""
          if collection2.find_one({"user id":self.userid}) != None:
               #user = collection2.find()[1]
               user = collection2.find_one({"user id":self.userid})
               name = user['name']
               Id = user['user id']
               access_token = user['access_token']
               self.actok = user['access_token']
               graph = facepy.GraphAPI(access_token)
               admin = facepy.GraphAPI(admin_token)
               nodes = []
               friends = []
               links =[]
               # get profile object
               user_name = graph.get('me')['name'].title()
               nodes.append({'name':user_name})
               linkIndex = 0
               nodeIndex = 1
               cursor1 = collection1.find({"large_id":Id})
               cursor1.batch_size(30)
               if (cursor1 != None):
                 for doc in cursor1:
                   if({'name':doc['small_name']} not in nodes): 	
                     interactions = {}
                     interactions["source"] = user_name
                     message = []                  
                     nodes.append({'name':doc['small_name']})
                     interactions['target']=doc['small_name']
                     self.createJson(user_name,doc,graph,interactions,message,nodes,links,linkIndex,admin,access_token)
                     linkIndex += 1
                     collection3.insert_one(interactions)
               cursor3 = collection1.find({"small_id":Id})
               cursor3.batch_size(30)
               if (cursor3 != None):
                 for doc in cursor3:
                   if ({'name':doc['large_name']} not in nodes):                
                     interactions = {}
                     interactions["source"] = user_name
                     message = []
                     nodes.append({'name':doc['large_name']})
                     interactions['target']=doc['large_name']
                     self.createJson(user_name,doc,graph,interactions,message,nodes,links,linkIndex,admin,access_token)
                     linkIndex += 1
                     collection3.insert_one(interactions)


               cursor2 = collection1.find({"collected_from":{ "$in": [{'name':user_name,'id':Id}] }})
               cursor2.batch_size(30);
               for doc in cursor2:
                 if (doc["large_id"] != Id and doc["small_id"] != Id):
                  if ({'name':doc['large_name']} not in nodes):
                      #interactions = {}
                      nodes.append({'name':doc['large_name']})
                      #interactions['source']=user_name
                      #interactions['target']=doc['large_name']
                      #try:
                         #collection3.insert_one(interactions)
                      #except:
                         #print "Interaction exists:"+doc['large_name']

                  if ({'name':doc['small_name']} not in nodes):
                      #interactions = {}
                      nodes.append({'name':doc['small_name']})
                      #interactions['source']=user_name
                      #interactions['target']=doc['small_name']
                      #try:
                         #collection3.insert_one(interactions)
                      #except:
                         #print "interaction exists:"+doc['small_name']
                  
                  interactions = {}
                  interactions['source'] = doc["large_name"]
                  message = []
                  interactions['target'] = doc["small_name"]

                  #if (collection3.find_one({"source":doc["large_name"],"target":doc["small_name"]}) != None):
                        # collection3.delete_one(collection3.find_one({"source":doc["large_name"],"target":doc["small_name"]}))
                  #if (collection3.find_one({"source":doc["small_name"],"target":doc["large_name"]}) != None):
                       # collection3.delete_one(collection3.find_one({"source":doc["small_name"],"target":doc["large_name"]}))

                  if (doc != {} and doc != None):
                      self.createJson(user_name,doc,graph,interactions,message,nodes,links,linkIndex,admin,access_token)
                  linkIndex += 1

                  collection3.insert_one(interactions)

               print "Done"
               jsons = {'nodes':nodes,'links':links}
               try :
                  user['json'] = jsons
                  collection2.update({"user id":self.userid},user)
                  print collection2.find_one({"user id":self.userid})
                  print jsons 
                  print "Updated Collection"
               except :
                  lol = 1
               
    def sendNotification(self): 
        template = "Your network visualization is now ready. Click to view it !!"
        href = "https://apps.facebook.com/1582658458614337/viz.php?resp="+self.actok+"&user="+self.userid
        data = {"access_token":self.actok,"href":href,"template":template}
        postreq = "https://graph.facebook.com/v2.4/" + self.userid + "/notifications?access_token="+self.actok+"&amp;href="+href+"&amp;template="+template
        posturl = "https://graph.facebook.com/v2.4/" + self.userid + "/notifications"
        requests.post(postreq)

    def add_to_link(self,source,target,num,nodes,links,linkIndex):
       try:
           links[linkIndex]['value'] = links[linkIndex]['value'] + num
       except:
           links.append({'source':nodes.index({"name":source}) , 'target':nodes.index({"name":target}) , 'value':num}) 

    def getIndex(self,name,nodes):
       i=0
       for node in nodes:
          if node['name']==name:
            return i
           
          i = i+1

    def contains(self,target,nodes):
        for node in nodes:
            if node['name']==target:
                return True
        return False

    def createVideo(self,link):            
             video = '<div class="fb-video" data-href='+link+' data-width="50"></div>'
             return video
              
    def getPosts(self,graph,posts,user_name,nodes,links,otherLinks):
         data = posts['data']
         dup = posts
         nextData = pagingData(dup,graph)
         data.extend(nextData)
         notReq = ["added_photos","tagged_in_photo","approved_friend","created_group","created_event"]
         for post in data:
             story = description = video = Postmsg = link = picture = ""
             BdayMsg = False
             storyTags = msgTags = {}
             message = []


    def createPostsMessage(self,post,interactionType):
            notReq = ["added_photos","tagged_in_photo","approved_friend","created_group","created_event"]
            message = []
            BdayMsg = False
            status_type = ""
            Postmsg = ""
            story = ""
            link = ""
            description = ""
            picture = "" 
            video = ""
            if ('status_type' in post):
                status_type = post['status_type']
            if ('message' in post):
                Postmsg = post['message']
            if ('story' in post):
                story = post['story']
            if (story.find("others wrote on your timeline") != -1):
                BdayMsg = True
            if ('link' in post): 
                link = post['link']
            if ('description' in post):
                description = post['description']
            if ('picture' in post):
                picture = post['picture']
            if ('created_time' in post): 
                date = dateparser.parse(post['created_time']).strftime('%m/%d/%y')
            if (status_type == 'added_video'):
                video = self.createVideo(link)    
            if (BdayMsg == True and (interactionType == "large_posts_post_to_small_timeline_id" or interactionType == "small_posts_post_to_large_timeline_id")):
                message = ["post","Bday",story,Postmsg,description,link,picture,video,date]
            else:
                message = ["post",status_type,interactionType,story,Postmsg,description,link,picture,video,date]
	    print message
        
            return message       
                 
    def addMsg(self,message,interactions):
        if ('data' not in interactions.keys()):
                interactions['data']=[message]
        else : 
                interactions['data'].append(message)



    def createJson(self,user_name,doc,graph,interactions,message,nodes,links,linkIndex,admin,access_token):
          fb = "https://graph.facebook.com/v2.4/"
          image = ""

          #PHOTOS
          if ('large_likes_small_photo_id_action' in doc):    
              if (doc['large_likes_small_photo_id_action'] != [] and doc['large_likes_small_photo_id_action'] != "NA"):
                      for photo in doc['large_likes_small_photo_id_action']:
                            try:
                                photoId = photo['id']
                                url = fb+photoId+"?fields=picture,created_time&access_token="+access_token
                                photoData = requests.get(url).json()
                                date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in photoData):
                                    image = photoData['picture']
                                message = ["photo","large_likes_small_action",image,date]
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_likes_small_photo_id_action'
                                print str(e)
                                print photoId
                            self.add_to_link(doc['large_name'],doc['small_name'],2,nodes,links,linkIndex) 


          if ('small_likes_large_photo_id_action' in doc):    
              if (doc['small_likes_large_photo_id_action'] != [] and doc['small_likes_large_photo_id_action'] != "NA"):
                      for photo in doc['small_likes_large_photo_id_action']:
                            try:
                                photoId = photo['id']    
                                fields = "fields=created_time,from,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+photoId+"?fields=picture,created_time&access_token="+access_token
                                photoData = requests.get(url).json()
                                date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in photoData):
                                    image = photoData['picture']
                                message = ["photo","small_likes_large_action",image,date]
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_likes_large_photo_id_action'
                                print str(e)
                                print photoId
                            self.add_to_link(doc['large_name'],doc['small_name'],2,nodes,links,linkIndex)    

          if ('large_likes_small_photo_id_timeline' in doc):    
              if (doc['large_likes_small_photo_id_timeline'] != [] and doc['large_likes_small_photo_id_timeline'] != "NA"):
                      for photo in doc['large_likes_small_photo_id_timeline']:
                            try:
                                photoId = photo['id']
                                fields = "fields=created_time,from,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+photoId+"?fields=picture,created_time&access_token="+access_token
                                photoData = requests.get(url).json()
                                date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in photoData):
                                    image = photoData['picture']                            
                                message = ["photo","large_likes_small_timeline",image,date]
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_likes_small_photo_id_timeline'
                                print str(e)
                                print photoId
                            self.add_to_link(doc['large_name'],doc['small_name'],2,nodes,links,linkIndex)

          if ('small_likes_large_photo_id_timeline' in doc):    
              if (doc['small_likes_large_photo_id_timeline'] != [] and doc['small_likes_large_photo_id_timeline'] != "NA"):
                      for photo in doc['small_likes_large_photo_id_timeline']:
                            try:
                                photoId = photo['id']    
                                fields = "fields=created_time,from,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+photoId+"?fields=picture,created_time&access_token="+access_token
                                photoData = requests.get(url).json()
                                date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in photoData):
                                    image = photoData['picture']
                                message = ["photo","small_likes_large_timeline",image,date]
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_likes_large_photo_id_timeline'
                                print str(e)
                                print photoId
                            self.add_to_link(doc['large_name'],doc['small_name'],2,nodes,links,linkIndex)

          if ('large_comments_on_small_photo_id_action' in doc):    
              if (doc['large_comments_on_small_photo_id_action'] != [] and doc['large_comments_on_small_photo_id_action'] != "NA"):
                      for photo in doc['large_comments_on_small_photo_id_action']:
                              try:
                                 photoId = photo['id']
                                 fields = "fields=created_time,from,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                 url = fb+photoId+"?fields=picture,created_time&access_token="+access_token
                                 photoData = requests.get(url).json()
                                 date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                                 if ('picture' in photoData):
                                    image = photoData['picture']
                                 message = ["photo","large_comments_on_small_action",image,date]
                                 self.addMsg(message,interactions)
                                 
                              except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_comments_on_small_photo_id_action'
                                print str(e)
                                print photoId
                              self.add_to_link(doc['large_name'],doc['small_name'],3,nodes,links,linkIndex)
                                
          
          if ('small_comments_on_large_photo_id_action' in doc):    
              if (doc['small_comments_on_large_photo_id_action'] != [] and doc['small_comments_on_large_photo_id_action'] != "NA"):
                      for photo in doc['small_comments_on_large_photo_id_action']:
                            try:
                                 photoId = photo['id']
                                 fields = "fields=created_time,from,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                 url = fb+photoId+"?fields=picture,created_time&access_token="+access_token
                                 photoData = requests.get(url).json()
                                 date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                                 if ('picture' in photoData):
                                    image = photoData['picture']
                                 message = ["photo","small_comments_on_large_action",image,date]
                                 self.addMsg(message,interactions)
                                 
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_comments_on_large_photo_id_action'
                                print str(e)
                                print photoId
                            self.add_to_link(doc['large_name'],doc['small_name'],3,nodes,links,linkIndex)
                                

          if ('large_comments_on_small_photo_id_timeline' in doc):    
              if (doc['large_comments_on_small_photo_id_timeline'] != [] and doc['large_comments_on_small_photo_id_timeline'] != "NA"):
                      for photo in doc['large_comments_on_small_photo_id_timeline']:
                            try:
                                 photoId = photo['id']
                                 fields = "fields=created_time,from,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                 url = fb+photoId+"?fields=picture,created_time&access_token="+access_token
                                 photoData = requests.get(url).json()
                                 date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                                 if ('picture' in photoData):
                                    image = photoData['picture']
                                 message = ["photo","large_comments_on_small_timeline",image,date]
                                 self.addMsg(message,interactions)
                                 
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_comments_on_small_photo_id_timeline'
                                print str(e)
                                print photoId
                            self.add_to_link(doc['large_name'],doc['small_name'],3,nodes,links,linkIndex)
                                

          if ('small_comments_on_large_photo_id_timeline' in doc):    
              if (doc['small_comments_on_large_photo_id_timeline'] != [] and doc['small_comments_on_large_photo_id_timeline'] != "NA"):
                      for photo in doc['small_comments_on_large_photo_id_timeline']:
                            try:
                                 photoId = photo['id']
                                 fields = "fields=created_time,from,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                 url = fb+photoId+"?fields=picture,created_time&access_token="+access_token
                                 photoData = requests.get(url).json()
                                 date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                                 if ('picture' in photoData):
                                    image = photoData['picture']
                                 message = ["photo","small_comments_on_large_timeline",image,date]
                                 self.addMsg(message,interactions)
                                 
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_comments_on_large_photo_id_timeline'
                                print str(e)
                                print photoId
                            self.add_to_link(doc['large_name'],doc['small_name'],3,nodes,links,linkIndex)
                                

          if ('large_is_tagged_in_small_photo_id_action' in doc):  
              if (doc['large_is_tagged_in_small_photo_id_action'] != [] and doc['large_is_tagged_in_small_photo_id_action'] != "NA"):
                      for photo in doc['large_is_tagged_in_small_photo_id_action']:
                            try:
                                photoId = photo['id']
                                fields = "fields=created_time,from,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+photoId+"?fields=picture,created_time&access_token="+access_token
                                photoData = requests.get(url).json()
                                date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in photoData):
                                    image = photoData['picture']
                                message = ["photo","large_tagged_in_small_action",image,date]
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_is_tagged_in_small_photo_id_action'
                                print str(e)
                                print photoId
                            self.add_to_link(doc['large_name'],doc['small_name'],4,nodes,links,linkIndex)
                                

          if ('small_is_tagged_in_large_photo_id_action' in doc):  
              if (doc['small_is_tagged_in_large_photo_id_action'] != [] and doc['small_is_tagged_in_large_photo_id_action'] != "NA"):
                      for photo in doc['small_is_tagged_in_large_photo_id_action']:
                            try:
                                photoId = photo['id']
                                fields = "fields=created_time,from,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+photoId+"?fields=picture,created_time&access_token="+access_token
                                photoData = requests.get(url).json()
                                date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in photoData):
                                    image = photoData['picture']
                                message = ["photo","small_tagged_in_large_action",image,date]
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_is_tagged_in_large_photo_id_action'
                                print str(e)
                                print photoId
                            self.add_to_link(doc['large_name'],doc['small_name'],4,nodes,links,linkIndex)
                                

          if ('large_is_tagged_in_small_photo_id_timeline' in doc):  
              if (doc['large_is_tagged_in_small_photo_id_timeline'] != [] and doc['large_is_tagged_in_small_photo_id_timeline'] != "NA"):
                      for photo in doc['large_is_tagged_in_small_photo_id_timeline']:
                            try:
                                photoId = photo['id']
                                fields = "fields=created_time,from,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+photoId+"?fields=picture,created_time&access_token="+access_token
                                photoData = requests.get(url).json()
                                date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in photoData):
                                    image = photoData['picture']
                                message = ["photo","large_tagged_in_small_timeline",image,date]
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_is_tagged_in_small_photo_id_timeline'
                                print str(e)
                                print photoId
                            self.add_to_link(doc['large_name'],doc['small_name'],4,nodes,links,linkIndex)
                                

          if ('small_is_tagged_in_small_photo_id_timeline' in doc):  
              if (doc['small_is_tagged_in_large_photo_id_timeline'] != [] and doc['small_is_tagged_in_large_photo_id_timeline'] != "NA"):
                      for photo in doc['small_is_tagged_in_large_photo_id_timeline']:
                          try:
                                photoId = photo['id']
                                fields = "fields=created_time,from,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+photoId+"?fields=picture,created_time&access_token="+access_token
                                photoData = requests.get(url).json()
                                date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in photoData):
                                    image = photoData['picture']
                                message = ["photo","small_tagged_in_large_timeline",image,date]
                                self.addMsg(message,interactions)
                                
                          except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_is_tagged_in_large_photo_id_timeline'
                                print str(e)
                                print photoId
                                
                          self.add_to_link(doc['small_name'],doc['large_name'],4,nodes,links,linkIndex)

          if ('co_like_photo_id' in doc):                     
              if (doc['co_like_photo_id'] != [] and doc['co_like_photo_id'] != "NA"):
                      for photo in doc['co_like_photo_id']:
                            try:
                                 photoId = photo['id']
                                 fields = "fields=created_time,from,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                 url = fb+photoId+"?fields=picture,created_time&access_token="+access_token
                                 photoData = requests.get(url).json()
                                 #print photoId
                                 date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                                 if ('picture' in photoData):
                                    image = photoData['picture']
                                 message = ["photo","CoLike",image,date]
                                 self.addMsg(message,interactions)                          
                                 
                            except Exception,e:
                                 print doc['large_name']+","+doc['small_name']
                                 print 'co_like_photo_id'
                                 print str(e)
                                 print photoId
                                 self.add_to_link(doc['large_name'],doc['small_name'],1,nodes,links,linkIndex)
                                

          if ('co_comment_photo_id' in doc):                   
              if (doc['co_comment_photo_id'] != [] and doc['co_comment_photo_id'] != "NA"):
                      for photo in doc['co_comment_photo_id']:
                            try:
                                  photoId = photo['id']
                                  fields = "fields=created_time,from,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                  url = fb+photoId+"?fields=picture,created_time&access_token="+access_token
                                  photoData = requests.get(url).json()
                                  date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                                  if ('picture' in photoData):
                                    image = photoData['picture']
                                  message = ["photo","CoCommented",image,date]
                                  self.addMsg(message,interactions)
                                  
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'co_comment_photo_id'
                                print str(e)
                                print photoId
                            self.add_to_link(doc['large_name'],doc['small_name'],2,nodes,links,linkIndex)
                                
          
          if ('co_tagged_photo_id' in doc):                     
              if (doc['co_tagged_photo_id'] != [] and doc['co_tagged_photo_id'] != "NA"):
                      for photo in doc['co_tagged_photo_id']:
                              try:
                                  photoId = photo['id']
                                  fields = "fields=created_time,from,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                  url = fb+photoId+"?fields=picture,created_time&access_token="+access_token
                                  photoData = requests.get(url).json()
                                  date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                                  if ('picture' in photoData):
                                    image = photoData['picture']
                                  message = ["photo","CoTagged",image,date]
                                  self.addMsg(message,interactions)
                                   
                              except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'co_tagged_photo_id'
                                print str(e)
                                print photoId
                              self.add_to_link(doc['large_name'],doc['small_name'],5,nodes,links,linkIndex)
                                
              
          #POSTS 
          if ('large_likes_small_post_id_action' in doc):    
              if (doc['large_likes_small_post_id_action'] != [] and doc['large_likes_small_post_id_action'] != "NA"):
                      for post in doc['large_likes_small_post_id_action']:
                            try:
                                postId = post['id']
                                fields = "fields=created_time,from,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                postData = requests.get(url).json()
                                date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in postData):
                                    image = postData['picture']
                                message = self.createPostsMessage(postData,"large_likes_small_action")
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_likes_small_post_id_action'
                                print str(e)
                                print postId
                            self.add_to_link(doc['large_name'],doc['small_name'],2,nodes,links,linkIndex)
                                
          if ('small_likes_large_post_id_action' in doc):    
              if (doc['small_likes_large_post_id_action'] != [] and doc['small_likes_large_post_id_action'] != "NA"):
                      for post in doc['small_likes_large_post_id_action']:
                            try:
                                postId = post['id']
                              
                                fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                postData = requests.get(url).json()
                                date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in postData):
                                    image = postData['picture']
                                message = self.createPostsMessage(postData,"small_likes_large_action")
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_likes_large_post_id_action'
                                print str(e)
                                print postId
                            self.add_to_link(doc['large_name'],doc['small_name'],2,nodes,links,linkIndex)
                                

          if ('large_likes_small_post_id_timeline' in doc):    
              if (doc['large_likes_small_post_id_timeline'] != [] and doc['large_likes_small_post_id_timeline'] != "NA"):
                      for post in doc['large_likes_small_post_id_timeline']:
                            try:
                                postId = post['id']
                                fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                postData = requests.get(url).json()
                                date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in postData):
                                    image = postData['picture']
                                message = self.createPostsMessage(postData,'large_likes_small_timeline')
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_likes_small_post_id_timeline'
                                print str(e)
                                print postId
                            self.add_to_link(doc['large_name'],doc['small_name'],2,nodes,links,linkIndex)
                                

          if ('small_likes_large_post_id_timeline' in doc):    
              if (doc['small_likes_large_post_id_timeline'] != [] and doc['small_likes_large_post_id_timeline'] != "NA"):
                      for post in doc['small_likes_large_post_id_timeline']:
                            try:
                                postId = post['id']
                                fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                postData = requests.get(url).json()
                                date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in postData):
                                    image = postData['picture']
                                message = self.createPostsMessage(postData,'small_likes_large_timeline')
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_likes_large_post_id_timeline'
                                print str(e)
                                print postId
                            self.add_to_link(doc['large_name'],doc['small_name'],2,nodes,links,linkIndex)
                                

          if ('large_comments_on_small_post_id_action' in doc):    
              if (doc['large_comments_on_small_post_id_action'] != [] and doc['large_comments_on_small_post_id_action'] != "NA"):
                      for post in doc['large_comments_on_small_post_id_action']:
                              try:
                                 postId = post['id']
                                 fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                 url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                 postData = requests.get(url).json()
                                 date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                 if ('picture' in postData):
                                    image = postData['picture']
                                 message = self.createPostsMessage(postData,"large_comments_on_small_action")
                                 self.addMsg(message,interactions)
                                 
                              except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_comments_on_small_post_id_action'
                                print str(e)
                                print postId
                              self.add_to_link(doc['large_name'],doc['small_name'],3,nodes,links,linkIndex)
                                
          
          if ('small_comments_on_large_post_id_action' in doc):    
              if (doc['small_comments_on_large_post_id_action'] != [] and doc['small_comments_on_large_post_id_action'] != "NA"):
                      for post in doc['small_comments_on_large_post_id_action']:
                              try:
                                 postId = post['id']
                                 fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                 url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                 postData = requests.get(url).json()
                                 date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                 if ('picture' in postData):
                                    image = postData['picture']
                                 message = self.createPostsMessage(postData,"small_comments_on_large_action")
                                 self.addMsg(message,interactions)
                                 
                              except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_comments_on_large_post_id_action'
                                print str(e)
                                print postId
                              self.add_to_link(doc['large_name'],doc['small_name'],3,nodes,links,linkIndex)
                                

          if ('large_comments_on_small_post_id_timeline' in doc):    
              if (doc['large_comments_on_small_post_id_timeline'] != [] and doc['large_comments_on_small_post_id_timeline'] != "NA"):
                      for post in doc['large_comments_on_small_post_id_timeline']:
                              try:
                                 postId = post['id']
                                 fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                 url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                 postData = requests.get(url).json()
                                 date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                 if ('picture' in postData):
                                    image = postData['picture']
                                 message = self.createPostsMessage(postData,"large_comments_on_small_timeline")
                                 self.addMsg(message,interactions)
                                 
                              except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_comments_on_small_post_id_timeline'
                                print str(e)
                                print postId
                              self.add_to_link(doc['large_name'],doc['small_name'],3,nodes,links,linkIndex)
                                

          if ('small_comments_on_large_post_id_timeline' in doc):    
              if (doc['small_comments_on_large_post_id_timeline'] != [] and doc['small_comments_on_large_post_id_timeline'] != "NA"):
                      for post in doc['small_comments_on_large_post_id_timeline']:
                              try:
                                 postId = post['id']
                                 fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                 url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                 postData = requests.get(url).json()
                                 date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                 if ('picture' in postData):
                                    image = postData['picture']
                                 message = self.createPostsMessage(postData,"small_comments_on_large_timeline")
                                 self.addMsg(message,interactions)
                                 
                              except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_comments_on_large_post_id_timeline'
                                print str(e)
                                print postId
                              self.add_to_link(doc['large_name'],doc['small_name'],3,nodes,links,linkIndex)

          if ('large_is_tagged_in_small_post_id_action' in doc):  
              if (doc['large_is_tagged_in_small_post_id_action'] != [] and doc['large_is_tagged_in_small_post_id_action'] != "NA"):
                      for post in doc['large_is_tagged_in_small_post_id_action']:
                            try:
                                postId = post['id']
                                fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                postData = requests.get(url).json()
                                date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in postData):
                                    image = postData['picture']
                                message = self.createPostsMessage(postData,"large_tagged_in_small_action")
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_is_tagged_in_small_post_id_action'
                                print str(e)
                                print postId
                            self.add_to_link(doc['large_name'],doc['small_name'],4,nodes,links,linkIndex)
                                

          if ('small_is_tagged_in_large_post_id_action' in doc):  
              if (doc['small_is_tagged_in_large_post_id_action'] != [] and doc['small_is_tagged_in_large_post_id_action'] != "NA"):
                      for post in doc['small_is_tagged_in_large_post_id_action']:
                            try:
                                postId = post['id']
                                fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                postData = requests.get(url).json()
                                date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in postData):
                                    image = postData['picture']
                                message = self.createPostsMessage(postData,"small_tagged_in_large_action")
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_is_tagged_in_large_post_id_action'
                                print str(e)
                                print postId
                            self.add_to_link(doc['large_name'],doc['small_name'],4,nodes,links,linkIndex)
                                

          if ('large_is_tagged_in_small_post_id_timeline' in doc):  
              if (doc['large_is_tagged_in_small_post_id_timeline'] != [] and doc['large_is_tagged_in_small_post_id_timeline'] != "NA"):
                      for post in doc['large_is_tagged_in_small_post_id_timeline']:
                            try:
                                postId = post['id']
                                fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                postData = requests.get(url).json()
                                date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in postData):
                                    image = postData['picture']
                                message = self.createPostsMessage(postData,"large_tagged_in_small_timeline")
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_is_tagged_in_small_post_id_timeline'
                                print str(e)
                                print postId
                            self.add_to_link(doc['large_name'],doc['small_name'],4,nodes,links,linkIndex)
                                

          if ('small_is_tagged_in_large_post_id_timeline' in doc):  
              if (doc['small_is_tagged_in_large_post_id_timeline'] != [] and doc['small_is_tagged_in_large_post_id_timeline'] != "NA"):
                      for post in doc['small_is_tagged_in_large_post_id_timeline']:
                            try:
                                postId = post['id']
                                fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                postData = requests.get(url).json()
                                date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in postData):
                                    image = postData['picture']
                                message = self.createPostsMessage(postData,"small_tagged_in_large_timeline")
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_is_tagged_in_large_post_id_timeline'
                                print str(e)
                                print postId
                            self.add_to_link(doc['small_name'],doc['large_name'],4,nodes,links,linkIndex)
                                


          if ('co_like_post_id' in doc):                     
              if (doc['co_like_post_id'] != [] and doc['co_like_post_id'] != "NA"):
                      for post in doc['co_like_post_id']:
                            try:
                                 postId = post['id']
                                 fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                 url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                 postData = requests.get(url).json()
                                 date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                 if ('picture' in postData):
                                    image = postData['picture']
                                 message = self.createPostsMessage(postData,"CoLike")
                                 self.addMsg(message,interactions)
                                 
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'co_like_post_id'
                                print str(e)
                                print postId
                            self.add_to_link(doc['large_name'],doc['small_name'],1,nodes,links,linkIndex)
                                

          if ('co_comment_post_id' in doc):                   
              if (doc['co_comment_post_id'] != [] and doc['co_comment_post_id'] != "NA"):
                      for post in doc['co_comment_post_id']:
                            try:
                                  postId = post['id']
                                  fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                  url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                  postData = requests.get(url).json()
                                  date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                  if ('picture' in postData):
                                    image = postData['picture']
                                  message = self.createPostsMessage(postData,"CoCommented")
                                  self.addMsg(message,interactions)
                                  
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'co_comment_post_id'
                                print str(e)
                                print postId
                            self.add_to_link(doc['large_name'],doc['small_name'],2,nodes,links,linkIndex)
                                
          
          if ('co_tagged_post_id' in doc):                     
              if (doc['co_tagged_post_id'] != [] and doc['co_tagged_post_id'] != "NA"):
                      for post in doc['co_tagged_post_id']:
                            try:
                                  postId = post['id']
                                  fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                  url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                  postData = requests.get(url).json()
                                  date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                  if ('picture' in postData):
                                    image = postData['picture']
                                  message = self.createPostsMessage(postData,"CoTagged")
                                  self.addMsg(message,interactions)
                                   
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'co_tagged_post_id'
                                print str(e)
                                print postId
                            self.add_to_link(doc['large_name'],doc['small_name'],5,nodes,links,linkIndex)
                                

          if ('large_posts_post_to_small_timeline_id' in doc):                     
              if (doc['large_posts_post_to_small_timeline_id'] != [] and doc['large_posts_post_to_small_timeline_id'] != "NA"):
                      for post in doc['large_posts_post_to_small_timeline_id']:
                            try:
                                  postId = post['id']
                                  fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                  url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                  postData = requests.get(url).json()
                                  date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                  if ('picture' in postData):
                                    image = postData['picture']
                                  message = self.createPostsMessage(postData,"large_posts_to_small")
                                  self.addMsg(message,interactions)
                                  
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_posts_post_to_small_timeline_id'
                                print str(e)
                                print postId
                            self.add_to_link(doc['large_name'],doc['small_name'],5,nodes,links,linkIndex)
                                
          if ('small_posts_post_to_large_timeline_id' in doc):                     
              if (doc['small_posts_post_to_large_timeline_id'] != [] and doc['small_posts_post_to_large_timeline_id'] != "NA"):
                      for post in doc['small_posts_post_to_large_timeline_id']:
                              try:
                                  postId = post['id']
                                  fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                  url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                  postData = requests.get(url).json()
                                  date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                  if ('picture' in postData):
                                    image = postData['picture']
                                  message = self.createPostsMessage(postData,"small_posts_to_large")
                                  self.addMsg(message,interactions)
                                  
                              except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_posts_post_to_large_timeline_id'
                                print str(e)
                                print postId
                              self.add_to_link(doc['large_name'],doc['small_name'],5,nodes,links,linkIndex)
                                 

          if ('small_posts_photo_video_to_large_timeline_id' in doc):                     
              if (doc['small_posts_photo_video_to_large_timeline_id'] != [] and doc['small_posts_photo_video_to_large_timeline_id'] != "NA"):
                      for post in doc['small_posts_photo_video_to_large_timeline_id']:
                              try:
                                  postId = post['id']
                                  fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                  url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                  postData = requests.get(url).json()
                                  date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                  if ('picture' in postData):
                                    image = postData['picture']
                                  message = self.createPostsMessage(postData,"small_posts_to_large")
                                  self.addMsg(message,interactions)
                                   
                              except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_posts_photo_video_to_large_timeline_id'
                                print str(e)
                                print postId
                              self.add_to_link(doc['large_name'],doc['small_name'],5,nodes,links,linkIndex)
                                
          if ('large_posts_photo_video_to_small_timeline_id' in doc):                     
              if (doc['large_posts_photo_video_to_small_timeline_id'] != [] and doc['large_posts_photo_video_to_small_timeline_id'] != "NA"):
                      for post in doc['large_posts_photo_video_to_small_timeline_id']:
                            try:
                                  postId = post['id']
                                  fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                  url = fb+postId+"?fields=created_time,picture,story,message&access_token="+access_token
                                  postData = requests.get(url).json()
                                  date = dateparser.parse(postData['created_time']).strftime('%m/%d/%y')
                                  if ('picture' in postData):
                                    image = postData['picture']
                                  message = self.createPostsMessage(postData,"large_posts_to_small")
                                  self.addMsg(message,interactions)
                                  
                            except Exception,e: 
                                print doc['large_name']+","+doc['small_name']
                                print 'large_posts_photo_video_to_small_timeline_id'
                                print str(e)
                                print postId
                            self.add_to_link(doc['large_name'],doc['small_name'],5,nodes,links,linkIndex)

          #STATUSES
          if ('large_likes_small_status_id_action' in doc):    
              if (doc['large_likes_small_status_id_action'] != [] and doc['large_likes_small_status_id_action'] != "NA"):
                      for status in doc['large_likes_small_status_id_action']:
                            try:
                                statusId = status['id']
                                fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+statusId+"?fields=created_time,picture,story,message&access_token="+access_token
                                statusData = requests.get(url).json()
                                date = dateparser.parse(statusData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in statusData):
                                    image = statusData['picture']                            
                                message = self.createPostsMessage(statusData,"large_likes_small_action")
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_likes_small_status_id_action'
                                print str(e)
                                print statusId
                            self.add_to_link(doc['large_name'],doc['small_name'],2,nodes,links,linkIndex)
                                
          if ('small_likes_large_status_id_action' in doc):    
              if (doc['small_likes_large_status_id_action'] != [] and doc['small_likes_large_status_id_action'] != "NA"):
                      for status in doc['small_likes_large_status_id_action']:
                            try:
                                statusId = status['id']
                                fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+statusId+"?fields=created_time,picture,story,message&access_token="+access_token
                                statusData = requests.get(url).json()
                                date = dateparser.parse(statusData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in statusData):
                                    image = statusData['picture']                          
                                message = self.createPostsMessage(statusData,"small_likes_large_action")
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_likes_large_status_id_action'
                                print str(e)
                                print statusId
                            self.add_to_link(doc['large_name'],doc['small_name'],2,nodes,links,linkIndex)
                                

          if ('large_likes_small_status_id_timeline' in doc):    
              if (doc['large_likes_small_status_id_timeline'] != [] and doc['large_likes_small_status_id_timeline'] != "NA"):
                      for status in doc['large_likes_small_status_id_timeline']:
                            try:
                                statusId = status['id']
                                fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+statusId+"?fields=created_time,picture,story,message&access_token="+access_token
                                statusData = requests.get(url).json()
                                date = dateparser.parse(statusData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in statusData):
                                    image = statusData['picture']                          
                                message = self.createPostsMessage(statusData,"large_likes_small_timeline")
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_likes_small_status_id_timeline'
                                print str(e)
                                print statusId
                            self.add_to_link(doc['large_name'],doc['small_name'],2,nodes,links,linkIndex)


          if ('small_likes_large_status_id_timeline' in doc):    
              if (doc['small_likes_large_status_id_timeline'] != [] and doc['small_likes_large_status_id_timeline'] != "NA"):
                      for status in doc['small_likes_large_status_id_timeline']:
                            try:
                                statusId = status['id']
                              
                                fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+statusId+"?fields=created_time,picture,story,message&access_token="+access_token
                                statusData = requests.get(url).json()
                                date = dateparser.parse(statusData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in statusData):
                                    image = statusData['picture']                           
                                message = self.createPostsMessage(statusData,'small_likes_large_timeline')
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_likes_large_status_id_timeline'
                                print str(e)
                                print statusId
                            self.add_to_link(doc['large_name'],doc['small_name'],2,nodes,links,linkIndex)
                                

          if ('large_comments_on_small_status_id_action' in doc):    
              if (doc['large_comments_on_small_status_id_action'] != [] and doc['large_comments_on_small_status_id_action'] != "NA"):
                      for status in doc['large_comments_on_small_status_id_action']:
                            try:
                                 statusId = status['id']
                                 fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                 url = fb+statusId+"?fields=created_time,picture,story,message&access_token="+access_token
                                 statusData = requests.get(url).json()
                                 date = dateparser.parse(statusData['created_time']).strftime('%m/%d/%y')
                                 if ('picture' in statusData):
                                    image = statusData['picture']                            
                                 message = self.createPostsMessage(statusData,"large_comments_on_small_action")
                                 self.addMsg(message,interactions)
                                 
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_comments_on_small_status_id_action'
                                print str(e)
                                print statusId
                            self.add_to_link(doc['large_name'],doc['small_name'],3,nodes,links,linkIndex)
                                
          
          if ('small_comments_on_large_status_id_action' in doc):    
              if (doc['small_comments_on_large_status_id_action'] != [] and doc['small_comments_on_large_status_id_action'] != "NA"):
                      for status in doc['small_comments_on_large_status_id_action']:
                              try:
                                 statusId = status['id']
                                 fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                 url = fb+statusId+"?fields=created_time,picture,story,message&access_token="+access_token
                                 statusData = requests.get(url).json()
                                 date = dateparser.parse(statusData['created_time']).strftime('%m/%d/%y')
                                 if ('picture' in statusData):
                                    image = statusData['picture']                       
                                 message = self.createPostsMessage(statusData,"small_comments_on_large_action")
                                 self.addMsg(message,interactions)
                                 
                              except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_comments_on_large_status_id_action'
                                print str(e)
                                print statusId
                              self.add_to_link(doc['large_name'],doc['small_name'],3,nodes,links,linkIndex)

          if ('large_comments_on_small_status_id_timeline' in doc):    
              if (doc['large_comments_on_small_status_id_timeline'] != [] and doc['large_comments_on_small_status_id_timeline'] != "NA"):
                      for status in doc['large_comments_on_small_status_id_timeline']:
                            try:
                                 statusId = status['id']
                                 fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                 url = fb+statusId+"?fields=created_time,picture,story,message&access_token="+access_token
                                 statusData = requests.get(url).json()
                                 date = dateparser.parse(statusData['created_time']).strftime('%m/%d/%y')
                                 if ('picture' in statusData):
                                    image = statusData['picture']                            
                                 message = self.createPostsMessage(statusData,"large_comments_on_small_timeline")
                                 self.addMsg(message,interactions)
                                 
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_comments_on_small_status_id_timeline'
                                print str(e)
                                print statusId
                            self.add_to_link(doc['large_name'],doc['small_name'],3,nodes,links,linkIndex)
                                

          if ('small_comments_on_large_status_id_timeline' in doc):    
              if (doc['small_comments_on_large_status_id_timeline'] != [] and doc['small_comments_on_large_status_id_timeline'] != "NA"):
                      for status in doc['small_comments_on_large_status_id_timeline']:
                            try:
                                 statusId = status['id'] 
                                 fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                 url = fb+statusId+"?fields=created_time,picture,story,message&access_token="+access_token
                                 statusData = requests.get(url).json()
                                 date = dateparser.parse(statusData['created_time']).strftime('%m/%d/%y')
                                 if ('picture' in statusData):
                                    image = statusData['picture']                           
                                 message = self.createPostsMessage(statusData,"small_comments_on_large_timeline")
                                 self.addMsg(message,interactions)
                                 
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_comments_on_large_status_id_timeline'
                                print str(e)
                                print statusId
                            self.add_to_link(doc['large_name'],doc['small_name'],3,nodes,links,linkIndex)
                                

          if ('large_is_tagged_in_small_status_id_action' in doc):  
              if (doc['large_is_tagged_in_small_status_id_action'] != [] and doc['large_is_tagged_in_small_status_id_action'] != "NA"):
                      for status in doc['large_is_tagged_in_small_status_id_action']:
                            try:
                                statusId = status['id']
                                fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+statusId+"?fields=created_time,picture,story,message&access_token="+access_token
                                statusData = requests.get(url).json()
                                date = dateparser.parse(statusData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in statusData):
                                    image = statusData['picture']                          
                                message = self.createPostsMessage(statusData,"large_tagged_in_small_action")
                                self.addMsg(message,interactions) 
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'large_is_tagged_in_small_status_id_action'
                                print str(e)
                                print statusId
                            self.add_to_link(doc['large_name'],doc['small_name'],4,nodes,links,linkIndex) 

          if ('small_is_tagged_in_large_status_id_action' in doc):  
              if (doc['small_is_tagged_in_large_status_id_action'] != [] and doc['small_is_tagged_in_large_status_id_action'] != "NA"):
                      for status in doc['small_is_tagged_in_large_status_id_action']:
                            try:
                                statusId = status['id']
                                fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+statusId+"?fields=created_time,picture,story,message&access_token="+access_token
                                statusData = requests.get(url).json()
                                date = dateparser.parse(statusData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in statusData):
                                    image = statusData['picture']                          
                                message = self.createPostsMessage(statusData,"small_tagged_in_large_action")
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_is_tagged_in_large_status_id_action'
                                print str(e)
                                print statusId
                            self.add_to_link(doc['large_name'],doc['small_name'],4,nodes,links,linkIndex)
                                

          if ('large_is_tagged_in_small_status_id_timeline' in doc):  
              if (doc['large_is_tagged_in_small_status_id_timeline'] != [] and doc['large_is_tagged_in_small_status_id_timeline'] != "NA"):
                      for status in doc['large_is_tagged_in_small_status_id_timeline']:
                            try:
                                statusId = status['id']
                                fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+statusId+"?fields=created_time,picture,story,message&access_token="+access_token
                                statusData = requests.get(url).json()
                                date = dateparser.parse(statusData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in statusData):
                                    image = statusData['picture']                           
                                message = self.createPostsMessage(statusData,"large_tagged_in_small_timeline")
                                self.addMsg(message,interactions)
                                
                            except:
                                print doc['large_name']+","+doc['small_name']
                                print statusId
                                print 'large_is_tagged_in_small_status_id_timeline'
                            self.add_to_link(doc['large_name'],doc['small_name'],4,nodes,links,linkIndex)
                                

          if ('small_is_tagged_in_large_status_id_timeline' in doc):  
              if (doc['small_is_tagged_in_large_status_id_timeline'] != [] and doc['small_is_tagged_in_large_status_id_timeline'] != "NA"):
                      for status in doc['small_is_tagged_in_large_status_id_timeline']:
                            try:
                                statusId = status['id']
                                fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                url = fb+statusId+"?fields=created_time,picture,story,message&access_token="+access_token
                                statusData = requests.get(url).json()
                                date = dateparser.parse(statusData['created_time']).strftime('%m/%d/%y')
                                if ('picture' in statusData):
                                    image = statusData['picture']                           
                                message = self.createPostsMessage(statusData,"small_tagged_in_large_timeline")
                                self.addMsg(message,interactions)
                                
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'small_is_tagged_in_large_status_id_timeline'
                                print str(e)
                                print statusId
                            self.add_to_link(doc['small_name'],doc['large_name'],4,nodes,links,linkIndex)
                                


          if ('co_like_status_id' in doc):                     
              if (doc['co_like_status_id'] != [] and doc['co_like_status_id'] != "NA"):
                      for status in doc['co_like_status_id']:
                            try:
                                 statusId = status['id']
                                 fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                 url = fb+statusId+"?fields=created_time,picture,story,message&access_token="+access_token
                                 statusData = requests.get(url).json()
                                 date = dateparser.parse(statusData['created_time']).strftime('%m/%d/%y')
                                 if ('picture' in statusData):
                                    image = statusData['picture']                             
                                 message = self.createPostsMessage(statusData,"CoLike")
                                 self.addMsg(message,interactions)
                                 
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'co_like_status_id'
                                print str(e)
                                print statusId
                            self.add_to_link(doc['large_name'],doc['small_name'],1,nodes,links,linkIndex)
                                

          if ('co_comment_status_id' in doc):                   
              if (doc['co_comment_status_id'] != [] and doc['co_comment_status_id'] != "NA"):
                      for status in doc['co_comment_status_id']:
                            try:
                                  statusId = status['id']
                                  fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                  url = fb+statusId+"?fields=created_time,picture,story,message&access_token="+access_token
                                  statusData = requests.get(url).json()
                                  date = dateparser.parse(statusData['created_time']).strftime('%m/%d/%y')
                                  if ('picture' in statusData):
                                    image = statusData['picture']                            
                                  message = self.createPostsMessage(statusData,"CoCommented")
                                  self.addMsg(message,interactions)
                                  
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'co_comment_status_id'
                                print str(e)
                                print statusId
                            self.add_to_link(doc['large_name'],doc['small_name'],2,nodes,links,linkIndex)
                                
          
          if ('co_tagged_status_id' in doc):                     
              if (doc['co_tagged_status_id'] != [] and doc['co_tagged_status_id'] != "NA"):
                      for status in doc['co_tagged_status_id']:
                            try:
                                  statusId = status['id']
                                  fields = "fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}"
                                  url = fb+statusId+"?fields=created_time,picture,story,message&access_token="+access_token
                                  statusData = requests.get(url).json()
                                  date = dateparser.parse(statusData['created_time']).strftime('%m/%d/%y')
                                  if ('picture' in statusData):
                                    image = statusData['picture']                            
                                  message = self.createPostsMessage(statusData,"CoTagged")
                                  self.addMsg(message,interactions)
                                  
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print 'co_tagged_status_id'
                                print str(e)
                                print statusId
                            self.add_to_link(doc['large_name'],doc['small_name'],5,nodes,links,linkIndex) 
                                

          #events 

          if ('co_attended_event_id' in doc):                    
              if (doc['co_attended_event_id'] != [] and doc['co_attended_event_id'] != "NA"):
                      for event in doc['co_attended_event_id']:
                            try:
                                 cover = description = date = ""
                                 eventId = event['id']
                                 fields="?fields=cover,description,start_time,name"
                                 url = fb+eventId+fields+"&access_token="+access_token
                                 eventData = requests.get(url).json()
                                 if ("cover" in eventData):
                                   cover = eventData["cover"]["source"] 
                                 name = eventData['name']
                                 if ("description" in eventData):
                                    description = eventData['description']
                                 date = dateparser.parse(eventData['start_time']).strftime('%m/%d/%y')  
                                 message = ["event",name,description,cover,date]
                                 self.addMsg(message,interactions)
                                 
                            except Exception,e:
                                print doc['large_name']+","+doc['small_name']
                                print "event"
                                print str(e)
                                print eventId
                            self.add_to_link(doc['large_name'],doc['small_name'],2,nodes,links,linkIndex) 
                                

          #Books and Music
          if ('co_like_id' in doc):                    
              if(doc['co_like_id'] != [] and doc['co_like_id'] != "NA"):
                      for x in doc['co_like_id']:
                              try:
                                 Id = x['id'] 
                                 about = name = pic = description = ""
                                 fields="?fields=about,name,picture,description,category"
                                 url = fb+Id+fields+"&access_token="+access_token
                                 Data = requests.get(url).json()
                                 if('about' in Data):
                                      about =  Data["about"]
                                 if ('name' in Data):
                                     name = Data['name']
                                 if ('picture' in Data):
                                     pic = Data['picture']['data']['url']
                                 if ("description" in Data):
                                    description = Data["description"]
                                 if ("book" in Data['category'] or "Book" in Data['category']):
                                     message = ["book",about,description,name,pic]
                                 if ("music" in Data['category'] or "Music" in Data['category']):
                                     message = ["music",about,description,name,pic]
                                 self.addMsg(message,interactions)
                                  
                              except:
                                print doc['large_name']+","+doc['small_name']
                                print "co-likes"
                                print Id
                              self.add_to_link(doc['large_name'],doc['small_name'],1,nodes,links,linkIndex)

          if ('data' in interactions):
                  interactions['data'].sort()
                  interactions['data'] = list(interactions['data'] for interactions['data'],_ in itertools.groupby(interactions['data']))
