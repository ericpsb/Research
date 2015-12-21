!/usr/bin/env python
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
import dateutil.parser as dateparser
import gridfs


''' def add_to_link(source ,target, num, nodes,links,message,otherLinks,user_name):
     flag=0
     if contains(target,nodes):
         if target != source:
           for link in links:
               if ((link['source']==getIndex(source,nodes) and link['target']==getIndex(target,nodes)) or (link['source']==getIndex(target,nodes) and link['target'] == getIndex(source,nodes))) :
                   link['value']=link['value']+num
                   flag = 1
                   if (source==user_name):
                        val = 0
                        for interaction in nodes[getIndex(target,nodes)]['interactions']:
                            if ("Commented" in interaction):
                                val=1
                        if (val == 0):
                            nodes[getIndex(target,nodes)]['interactions'].append(message)
                   elif (target==user_name):
                        val = 0
                        for interaction in nodes[getIndex(source,nodes)]['interactions']:
                            if ("Commented" in interaction):
                                val=1
                        if (val == 0):
                            nodes[getIndex(source,nodes)]['interactions'].append(message)
                   else : 
                        pair1 = ""+str(getIndex(source,nodes))+","+str(getIndex(target,nodes))
                        if (pair1 in otherLinks):
                           otherLinks[pair1].append(message)
                        else:
                           otherLinks[pair1]=[message]
                           
           if (flag ==0):
               links.append({'source':getIndex(source,nodes),'target':getIndex(target,nodes),'value':num})
               pair = ""+str(getIndex(source,nodes))+","+str(getIndex(target,nodes))
               otherLinks[pair] = [message]
     else : 
         nodes.append({'name':target,'interactions':[message]})
         links.append({'source':getIndex(source,nodes),'target':getIndex(target,nodes),'value':num}) '''


def add_to_link(source,target,num,nodes,links,linkIndex):
       try:
           links[linkIndex]['value'] = links[linkIndex]['value'] + num
       except:
           links.append({'source':nodes.index(source) , 'target':nodes.index(target) , 'value':num}) 

def getIndex(name,nodes):
    i=0
    for node in nodes:
        if node['name']==name:
            return i
           
        i = i+1

def contains(target,nodes):
    for node in nodes:
        if node['name']==target:
            return True
    return False

def pagingData(dup,graph):
  data = []
  try:     
     if ('paging' in dup):
       paging = dup['paging']
       if ('next' in dup['paging']):
        nextLink = dup['paging']['next']
        nextSplit = nextLink.rsplit('/')
        nextPage = nextSplit[4]+"/"+nextSplit[5]
        dup = graph.get(nextPage)
        while (dup['data'] != []): 
           for post in dup['data']:
	     data.append(post)
           if ('paging' in dup):
              paging = dup['paging']
	      nextLink = dup['paging']['next']
	      nextSplit = nextLink.rsplit('/')
	      nextPage = nextSplit[4]+"/"+nextSplit[5]
	      dup = graph.get(nextPage)
              
  except:
        lol = "Error"
  return data

def pagingLikesComments(dup,graph):
      data = []
      paging = dup['paging']
      if ('next' in paging):
         nextLink = dup['paging']['next']
         nextSplit = nextLink.rsplit('/')
         nextPage = nextSplit[4]+"/"+nextSplit[5]
         dup = graph.get(nextPage)
         for like in dup['data']:
           data.append(like)
      while ('next' in dup['paging']):
             nextLink = dup['paging']['next']
             nextSplit = nextLink.rsplit('/')
             nextPage = nextSplit[4]+"/"+nextSplit[5]
             dup = graph.get(nextPage)
             for like in dup['data']:
                 data.append(like)
      return data

def getPhotos(photos,user_name,nodes,links,otherLinks,graph):
   tag_friends=like_friends=comment_friends=[]
   data = photos['data']
   dup = photos
   nextData = pagingData(dup,graph)
   data.extend(nextData)
   i = 0
   for photo in data:
    from_friend= ""
    message = []
    date = dateparser.parse(photo['created_time']).strftime('%m/%d/%y')
    image = photo['images'][0]['source']
    if ('from' in photo):
      from_friend =photo['from']['name']
      if from_friend != user_name:
           message = ["photo",from_friend,"Tagged",image,date]
           add_to_link(user_name,from_friend,3,nodes,links,message,otherLinks,user_name)
      if ('tags' in photo):
         tags = photo['tags']
         data = pagingLikesComments(tags,graph)
         tags = photo['tags']['data']
         tags.extend(data)
         for tag in tags:
                 if (tag['name']!=user_name):
                      tag_friends.append(tag['name'])
                 if (tag['name'] != from_friend):
                      message = ["photo",tag['name'],"Cotagged",image,date]
                      add_to_link(user_name,tag['name'],4,nodes,links,message,otherLinks,user_name)
                 if (tag['name'] != user_name):
                      message = ["photo","ByTagged",image,date]
                      add_to_link(from_friend,tag['name'],3,nodes,links,message,otherLinks,user_name)
         if (tag_friends != []):
              for tag in tag_friends:
                    if (len(tag_friends[tag_friends.index(tag)+1:])) != 0:
                         for rem in tag_friends[tag_friends.index(tag)+1:]:
                             message = ["photo","Cotagged",image,date]
                             add_to_link(tag,rem,3,nodes,links,message,otherLinks,user_name)
      if ('likes' in photo):
        likes = photo['likes']
        data = pagingLikesComments(likes,graph)
        likes = photo['likes']['data']
        likes.extend(data)
        for like in likes:
           # if user_name != like['name']:
               message = ["photo",like['name'],"Liked",image,date]
               add_to_link(user_name,like['name'],3,nodes,links,message,otherLinks,user_name)
          # if from_friend != like['name']:
               if (from_friend != user_name):
                    if (like['name'] != user_name):
                         message = ["photo","ByLiked",image,date]
                    add_to_link(from_friend,like['name'],3,nodes,links,message,otherLinks,user_name)
      if ('comments' in photo):
        comments = photo['comments']
        data = pagingLikesComments(comments,graph)
        comments = photo['comments']['data']
        comments.extend(data)
        for comment in comments:
                commentedTime = dateparser.parse(comment['created_time']).strftime('%m/%d/%y')
           # if user_name != like['name'] :
                message = ["photo",comment['from']['name'],"Commented",image,commentedTime]
                add_to_link(user_name,comment['from']['name'],4,nodes,links,message,otherLinks,user_name)
           # if from_friend != like['name']:
                if (from_friend != user_name):
                   if (comment['from']['name'] != user_name):
                         message = ["photo","Bycommented",image,commentedTime]
                   add_to_link(from_friend,comment['from']['name'],4,nodes,links,message,otherLinks,user_name)
    i = i+1
    print i   


def createVideo(link):            
         video = '<div class="fb-video" data-href='+link+' data-width="50"></div>'
         return video
          
def getPosts(graph,posts,user_name,nodes,links,otherLinks):
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
         if ('status_type' in post):
           status_type = post['status_type']
           if (status_type not in notReq):
             from_name = post['from']['name']
             if ('message' in post):
                Postmsg = post['message']
             if ('story' in post):
                story = post['story']
                if (story.find("others wrote on your timeline") != -1):
                   BdayMsg = True
             if ('message_tags' in post):
                msgTags = post['message_tags']
             if ('story_tags' in post):
                storyTags = post['story_tags']
             if ('link' in post): 
                link = post['link']
             if ('description' in post):
                description = post['description']
             if ('picture' in post):
                picture = post['picture']
             date = dateparser.parse(post['created_time']).strftime('%m/%d/%y')
             if (status_type == 'added_video'):
                 video = createVideo(link)    
             if (from_name != user_name):
                if (BdayMsg == True):
                   message = ["post",from_name,"bday_msg",date]
                else:   
                   message = ["post",from_name,status_type,story,Postmsg,description,link,picture,video,date]
                add_to_link(user_name,from_name,5,nodes,links,message,otherLinks,user_name)
                    
             if (storyTags != {}):
                 tagKeys = storyTags.keys()
                 for key in tagKeys:
                     tags = storyTags[key]
                     for tag in tags:
                       if ('type' in tag):
                         if (tag['type'] == 'user' and tag['name'] != user_name and tag['name'] != from_name):
                             if (BdayMsg == True):
                                 message = ["post",tag['name'],"bday_msg",date]
                             else :
                                 message = ["post",tag['name'],"Tagged",story,Postmsg,description,link,picture,video,date]
                             add_to_link(user_name,tag['name'],4,nodes,links,message,otherLinks,user_name)
                             if (tag['name'] != from_name and tag['type'] == 'user' and from_name != user_name):
                                message = ["post","Bytagged",story,Postmsg,description,link,picture,video,date]
                                add_to_link(from_name,tag['name'],4,nodes,links,message,otherLinks,user_name) 
             if (msgTags != {}):
                 tagKeys = msgTags.keys()
                 for key in tagKeys:
                     tags = msgTags[key]
                     for tag in tags:
                       if ('type' in tag):
                         if (tag['type'] == 'user' and tag['name'] != user_name and tag['name'] != from_name):
                            if(BdayMsg == True):
                                 message = ["post",tag['name'],"bday_msg",date]
                            else:
                                 message = ["post",tag['name'],"Tagged",story,Postmsg,description,link,picture,video,date]
                            add_to_link(user_name,tag['name'],4,nodes,links,message,otherLinks,user_name)
                         if (tag['name'] != from_name and tag['type'] == 'user' and from_name != user_name):
                                message = ["post","Bytagged",story,Postmsg,description,link,picture,video,date]
                                add_to_link(from_name,tag['name'],4,nodes,links,message,otherLinks,user_name)

             likes = comments = []
             if ('likes' in post):
                 likes = post['likes'] 
                 data = pagingLikesComments(likes,graph)
                 likes = post['likes']['data']
                 likes.extend(data)

             if ('comments' in post):
                 comments = post['comments']
                 data = pagingLikesComments(comments,graph)
                 comments = post['comments']['data']
                 comments.extend(data)
             
             for like in likes:
                  
                  if (like['name'] != user_name):
                      message = ["post",like['name'],"Liked",story,Postmsg,description,link,picture,video]
                      add_to_link(user_name,like['name'],1,nodes,links,message,otherLinks,user_name)
                  if (like['name'] != from_name and from_name != user_name and like['name'] != user_name):
                      message = ["post","Byliked",story,Postmsg,description,link,picture,video]
                      add_to_link(from_name,like['name'],1,nodes,links,message,otherLinks,user_name)
                  
             for comment in comments:
                  commentedTime=dateparser.parse(comment['created_time']).strftime('%m/%d/%y')
                  if (comment['from']['name'] != user_name):
                      message = ["post",comment['from']['name'],"Commented",story,Postmsg,description,link,picture,video,commentedTime]
                      add_to_link(user_name,comment['from']['name'],3,nodes,links,message,otherLinks,user_name)      
                  if (comment['from']['name'] != from_name and from_name != user_name and comment['from']['name'] != user_name):
                      message = ["post","Bycommented",story,Postmsg,description,link,picture,video,commentedTime]
                      add_to_link(from_name,comment['from']['name'],2,nodes,links,message,otherLinks,user_name)
     print "yahoo2"

def main():
#Get user from Database
  client = MongoClient('localhost', 27017)
  db1 = client['FB_NoUse']
  collection1 = db1['interactions']
  db2 = client['fbapp-DB']
  collection2 = db2['fb-users'] 
  collection3 = db2['fb-interactions']

  for user in collection2.find():   
    name = user['name']
    Id = user['user id']  
    access_token = user['access_token']  
    graph = facepy.GraphAPI(access_token)
    nodes = []
    links =[]
    otherLinks={}
    tag_friends=[]
    like_friends=[]
    comment_friends=[]
    #get profile object
    user_name = graph.get('me')['name']
    nodes.append({'name':user_name})
    linkIndex = 0
    nodeIndex = 1
    interactions = {'source':user_name}
    for doc in collection1.find({'collected_from':[{'name':name },{'id':Id}]})
          nodes.append({'name':doc['nodeB']})
          interactions['target']=doc['nodeB']
          if (doc['A_liked_B_photo_id'] != [] and doc['A_liked_B_photo_id'] != "NA"):
                  for photo in doc['A_liked_B_photo_id']:
                         photoId = photo['id']
                         photoData = graph.get(photoId+"?fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}")
                         date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                         image = photoData['images'][0]['source']
                         message = ["photo","ALiked",image,date]
                         if ('data' in interactions.keys()):
                               interactions['data']=[message]
                         else : 
                               interaction['data'].append(message)
                         
                         add_to_link(user_name,doc['nodeB'],2,nodes,links,linkIndex)
          if (doc['A_comments_on_B_photo_id'] != [] and doc['A_comments_on_B_photo_id'] != "NA"):
                  for photo in doc['A_comments_on_B_photo_id']:
                         photoId = photo['id']
                         photoData = graph.get(photoId+"?fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}")
                         date = dateparser.parse(photoData['comments']['created_time']).strftime('%m/%d/%y')
                         image = photoData['images'][0]['source']
                         message = ["photo","ACommented",image,date]
                         if ('data' in interactions.keys()):
                               interactions['data']=[message]
                         else : 
                               interaction['data'].append(message)
                         add_to_link(user_name,doc['nodeB'],3,nodes,links,linkIndex)
          if (doc['A_tagged_in_B_photo_id'] != [] and doc['A_tagged_in_B_photo_id'] != "NA"):
                  for photo in doc['A_tagged_in_B_photo_id']:
                         photoId = photo['id']
                         photoData = graph.get(photoId+"?fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}")
                         date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                         image = photoData['images'][0]['source']
                         message = ["photo","ATagged",image,date]
                         if ('data' in interactions.keys()):
                               interactions['data']=[message]
                         else : 
                               interaction['data'].append(message)
                         add_to_link(user_name,doc['nodeB'],4,nodes,links,linkIndex)
          if (doc['B_tagged_in_A_photo_id'] != [] and doc['B_tagged_in_A_photo_id'] != "NA"):
                  for photo in doc['B_tagged_in_A_photo_id']:
                         photoId = photo['id']
                         photoData = graph.get(photoId+"?fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}")
                         date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                         image = photoData['images'][0]['source']
                         message = ["photo","BTagged",image,date]
                         if ('data' in interactions.keys()):
                               interactions['data']=[message]
                         else : 
                               interaction['data'].append(message)
                         add_to_link(user_name,doc['nodeB'],4,nodes,links,linkIndex)
          if (doc['B_liked_A_photo_id'] != [] and doc['B_liked_A_photo_id'] != "NA"):
                  for photo in doc['B_liked_A_photo_id']:
                         photoId = photo['id']
                         photoData = graph.get(photoId+"?fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}")
                         date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                         image = photoData['images'][0]['source']
                         message = ["photo","BLiked",image,date]
                         if ('data' in interactions.keys()):
                               interactions['data']=[message]
                         else :
                               interaction['data'].append(message)

                         add_to_link(user_name,doc['nodeB'],2,nodes,links,linkIndex)
          if (doc['B_comments_on_A_photo_id'] != [] and doc['B_comments_on_A_photo_id'] != "NA"):
                  for photo in doc['B_comments_on_A_photo_id']:
                         photoId = photo['id']
                         photoData = graph.get(photoId+"?fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}")
                         date = dateparser.parse(photoData['comments']['created_time']).strftime('%m/%d/%y')
                         image = photoData['images'][0]['source']
                         message = ["photo","BCommented",image,date]
                         if ('data' in interactions.keys()):
                               interactions['data']=[message]
                         else : 
                               interaction['data'].append(message)
                         add_to_link(user_name,doc['nodeB'],3,nodes,links,linkIndex)
          if (doc['co_liked_photo_id'] != [] and doc['co_liked_photo_id'] != "NA"):
                  for photo in doc['co_liked_photo_id']:
                         photoId = photo['id']
                         photoData = graph.get(photoId+"?fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}")
                         date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                         image = photoData['images'][0]['source']
                         message = ["photo","CoLiked",image,date]
                         if ('data' in interactions.keys()):
                               interactions['data']=[message]
                         else :
                               interaction['data'].append(message)
                         add_to_link(user_name,doc['nodeB'],1,nodes,links,linkIndex)
          if (doc['co_commented_photo_id'] != [] and doc['co_commented_photo_id'] != "NA"):
                  for photo in doc['co_commented_photo_id']:
                         photoId = photo['id']
                         photoData = graph.get(photoId+"?fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}")
                         date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                         image = photoData['images'][0]['source']
                         message = ["photo","CoCommented",image,date]
                         if ('data' in interactions.keys()):
                               interactions['data']=[message]
                         else :
                               interaction['data'].append(message)
                         add_to_link(user_name,doc['nodeB'],2,nodes,links,linkIndex)
          if (doc['co_tagged_photo_id'] != [] and doc['co_tagged_photo_id'] != "NA"):
                  for photo in doc['co_tagged_photo_id']:
                         photoId = photo['id']
                         photoData = graph.get(photoId+"?fields=created_time,from,images,link,name,name_tags,picture,comments.limit(25){created_time,from},likes.limit(25){name},tags.limit(25){name}")
                         date = dateparser.parse(photoData['created_time']).strftime('%m/%d/%y')
                         image = photoData['images'][0]['source']
                         message = ["photo","CoTagged",image,date]
                         if ('data' in interactions.keys()):
                               interactions['data']=[message]
                         else :
                               interaction['data'].append(message)
                         add_to_link(user_name,doc['nodeB'],5,nodes,links,linkIndex) 
 
    
   

    posts = graph.get('me?fields=feed.limit(200){message,message_tags,from,source,created_time,story,story_tags,status_type,comments.limit(50){from,message,created_time},likes.limit(50){name},link,description,picture,type}')['feed']
    getPosts(graph,posts,user_name,nodes,links,otherLinks)
    jsons = {'nodes':nodes,'links':links,'otherLinks':otherLinks}
    try :
       collection.update(user,{"$set":{'json':jsons}})
    except :
       s = "vizJsons/"+user['user id'] + ".txt" 
       with open(s,'w') as outfile:
           json.dump(jsons, outfile)
       collection.update(user,{"$set":{'json':s}})
    print user
if __name__=="__main__":
     main()
