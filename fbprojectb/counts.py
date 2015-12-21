import pymongo
from pymongo import MongoClient


client = MongoClient('localhost', 27017)
db = client['FB_NoUse']
collection = db['interactions']
db2 = client['fbapp-DB']
collection2 = db2['fb-users']
collection3 = db2['fb-interactions']
user = collection2.find()[1]['name']
interactions = collection.find({'nodeA':user})
counts = 0
for doc in interactions:
    if ('A_likes_B_photo_count' in doc):    
          if (doc['A_likes_B_photo_count'] != [] and doc['A_likes_B_photo_count'] != "NA"):
              counts = counts + (2*doc['A_likes_B_photo_count'])
    if ('A_comments_on_B_photo_count' in doc):    
          if (doc['A_comments_on_B_photo_count'] != [] and doc['A_comments_on_B_photo_count'] != "NA"):
              counts = counts + (3*doc['A_comments_on_B_photo_count'])
    if ('A_tagged_in_B_photo_count' in doc):  
          if (doc['A_tagged_in_B_photo_count'] != [] and doc['A_tagged_in_B_photo_count'] != "NA"): 
          	    counts = counts + (4*doc['A_tagged_in_B_photo_count'])
    if ('B_tagged_in_A_photo_count' in doc):  
          if (doc['B_tagged_in_A_photo_count'] != [] and doc['B_tagged_in_A_photo_count'] != "NA"):
          	 counts = counts + (4*doc['B_tagged_in_A_photo_count'])
    if ('B_likes_A_photo_count' in doc):                     
          if (doc['B_likes_A_photo_count'] != [] and doc['B_likes_A_photo_count'] != "NA"):
          	 counts = counts + (2*doc['B_likes_A_photo_count'])
    if ('B_comments_on_A_photo_count' in doc):  
          if (doc['B_comments_on_A_photo_count'] != [] and doc['B_comments_on_A_photo_count'] != "NA"):
               counts = counts + (3*doc['B_comments_on_A_photo_count'])
    if ('co_liked_photo_count' in doc):                     
          if (doc['co_liked_photo_count'] != [] and doc['co_liked_photo_count'] != "NA"):
          	  counts = counts + (1*doc['co_liked_photo_count'])
    if ('co_commented_photo_count' in doc):                   
          if (doc['co_commented_photo_count'] != [] and doc['co_commented_photo_count'] != "NA"):
          	  counts = counts + (2*doc['co_commented_photo_count'])
    if ('co_tagged_photo_count' in doc):                     
          if (doc['co_tagged_photo_count'] != [] and doc['co_tagged_photo_count'] != "NA"):
          	  counts = counts + (5*doc['co_tagged_photo_count'])
    if ('A_likes_B_post_count' in doc):
          if (doc['A_likes_B_post_count'] != [] and doc['A_likes_B_post_count'] != "NA"):
          	 counts = counts + (2*doc['A_likes_B_post_count'])
    if ('A_comments_on_B_post_count' in doc):    
          if (doc['A_comments_on_B_post_count'] != [] and doc['A_comments_on_B_post_count'] != "NA"):
              counts = counts + (3*doc['A_comments_on_B_post_count'])
    if ('A_tagged_in_B_post_count' in doc):  
          if (doc['A_tagged_in_B_post_count'] != [] and doc['A_tagged_in_B_post_count'] != "NA"): 
          	    counts = counts + (4*doc['A_tagged_in_B_post_count'])
    if ('B_tagged_in_A_post_count' in doc):  
          if (doc['B_tagged_in_A_post_count'] != [] and doc['B_tagged_in_A_post_count'] != "NA"):
          	 counts = counts + (4*doc['B_tagged_in_A_post_count'])
    if ('B_likes_A_post_count' in doc):                     
          if (doc['B_likes_A_post_count'] != [] and doc['B_likes_A_post_count'] != "NA"):
          	 counts = counts + (2*doc['B_likes_A_post_count'])
    if ('B_comments_on_A_post_count' in doc):  
          if (doc['B_comments_on_A_post_count'] != [] and doc['B_comments_on_A_post_count'] != "NA"):
               counts = counts + (3*doc['B_comments_on_A_post_count'])
    if ('co_liked_post_count' in doc):                     
          if (doc['co_liked_post_count'] != [] and doc['co_liked_post_count'] != "NA"):
          	  counts = counts + (1*doc['co_liked_post_count'])
    if ('co_commented_post_count' in doc):                   
          if (doc['co_commented_post_count'] != [] and doc['co_commented_post_count'] != "NA"):
          	  counts = counts + (2*doc['co_commented_post_count'])
    if ('co_tagged_post_count' in doc):                     
          if (doc['co_tagged_post_count'] != [] and doc['co_tagged_post_count'] != "NA"):
          	  counts = counts + (5*doc['co_tagged_post_count'])
    if ('A_posts_on_B_timeline_count' in doc):                   
          if (doc['A_posts_on_B_timeline_count'] != [] and doc['A_posts_on_B_timeline_count'] != "NA"):
          	  counts = counts + (4*doc['A_posts_on_B_timeline_count'])
    if ('B_posts_on_A_timeline_count' in doc):                   
          if (doc['B_posts_on_A_timeline_count'] != [] and doc['B_posts_on_A_timeline_count'] != "NA"):
          	  counts = counts + (4*doc['B_posts_on_A_timeline_count'])
    if ('co_attended_event_count' in doc):                    
          if (doc['co_attended_event_count'] != [] and doc['co_attended_event_count'] != "NA"):
          	   counts = counts + (2*doc['co_attended_event_count'])
    if ('co_liked_book_count' in doc):                    
          if (doc['co_liked_book_count'] != [] and doc['co_liked_book_count'] != "NA"):
          	   counts = counts + (1*doc['co_liked_book_count'])
    if ('co_liked_music_count' in doc):                    
          if (doc['co_liked_music_count'] != [] and doc['co_liked_music_count'] != "NA"):
          	   counts = counts + (1*doc['co_liked_music_count'])

collection2.update(user,{"$set":{'count':count}})















