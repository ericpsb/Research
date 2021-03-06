#!/usr/bin/env python

import requests
import urllib2
import json
from apscheduler.scheduler import Scheduler
import pymongo
from pymongo import MongoClient
import time
# fixing the Insecure platform issue
import urllib3.contrib.pyopenssl
import dateutil.parser as dateparser
import gridfs
from itertools import combinations
import itertools
import config


class GenerateViz():

    def init(self, userid):
        self.userid = userid
        client = MongoClient(config.get_connection_string())
        db1 = client[config.FB_INFO_DB]
        collection1 = db1['interactions']
        db2 = client[config.USER_DB]
        collection2 = db2['fb-users']
        collection3 = db2['fb-interactions']
        if collection2.find_one({"user id": self.userid}) != None:
            #user = collection2.find()[1]
            user = collection2.find_one({"user id": self.userid})
            user_name = user['name']
            Id = user['user id']
            access_token = user['access_token']
            self.actok = user['access_token']
            nodes = []
            friends = []
            links = []
            nodes.append({'name': user_name})
            linkIndex = 0
            nodeIndex = 1
            cursor1 = collection1.find({"large_id": Id})
            cursor1.batch_size(30)
            if (cursor1 != None and cursor1.count() > 0):
                for doc in cursor1:
                    if({'name': doc['small_name']} not in nodes):
                        interactions = {}
                        interactions["source"] = user_name
                        message = []
                        nodes.append({'name': doc['small_name']})
                        interactions['target'] = doc['small_name']
                        self.createJson(doc, interactions, message, nodes, links, linkIndex, access_token, db1)
                        linkIndex += 1
                        collection3.insert_one(interactions)
            cursor1.close()
            cursor3 = collection1.find({"small_id": Id})
            cursor3.batch_size(30)
            if (cursor3 != None and cursor3.count() > 0):
                for doc in cursor3:
                    if ({'name': doc['large_name']} not in nodes):
                        interactions = {}
                        interactions["source"] = user_name
                        message = []
                        nodes.append({'name': doc['large_name']})
                        interactions['target'] = doc['large_name']
                        self.createJson(doc, interactions, message, nodes, links, linkIndex, access_token, db1)
                        linkIndex += 1
                        collection3.insert_one(interactions)
            cursor3.close()
            cursor2 = collection1.find(
                {"collected_from": {"$in": [{'name': user_name, 'id': Id}]}})
            cursor2.batch_size(30)
            if (cursor2 != None and cursor2.count() > 0):
                for doc in cursor2:
                    if (doc["large_id"] != Id and doc["small_id"] != Id):
                        if ({'name': doc['large_name']} not in nodes):
                            #interactions = {}
                            nodes.append({'name': doc['large_name']})
                            # interactions['source']=user_name
                            # interactions['target']=doc['large_name']
                            # try:
                            # collection3.insert_one(interactions)
                            # except:
                            # print "Interaction exists:"+doc['large_name']

                        if ({'name': doc['small_name']} not in nodes):
                            #interactions = {}
                            nodes.append({'name': doc['small_name']})
                            # interactions['source']=user_name
                            # interactions['target']=doc['small_name']
                            # try:
                            # collection3.insert_one(interactions)
                            # except:
                            # print "interaction exists:"+doc['small_name']

                        interactions = {}
                        interactions['source'] = doc["large_name"]
                        message = []
                        interactions['target'] = doc["small_name"]

                        # if (collection3.find_one({"source":doc["large_name"],"target":doc["small_name"]}) != None):
                        # collection3.delete_one(collection3.find_one({"source":doc["large_name"],"target":doc["small_name"]}))
                        # if (collection3.find_one({"source":doc["small_name"],"target":doc["large_name"]}) != None):
                        # collection3.delete_one(collection3.find_one({"source":doc["small_name"],"target":doc["large_name"]}))

                        if (doc != {} and doc != None):
                            self.createJson(doc, interactions, message, nodes, links, linkIndex, access_token, db1)
                        linkIndex += 1

                        collection3.insert_one(interactions)
            cursor2.close()

            print "Done"
            jsons = {'nodes': nodes, 'links': links}
            try:
                user['json'] = jsons
                collection2.update({"user id": self.userid}, user)
                # print collection2.find_one({"user id": self.userid})
                # print jsons
                print "Updated Collection"
            except:
                lol = 1

    def add_to_link(self, source, target, num, nodes, links, linkIndex):
        try:
            links[linkIndex]['value'] = links[linkIndex]['value'] + num
        except:
            links.append({'source': nodes.index({"name": source}),
                          'target': nodes.index({"name": target}), 'value': num})

    def createVideo(self, link):
        video = '<div class="fb-video" data-href=' + link + ' data-width="50"></div>'
        return video

    def createPostsMessage(self, post, interactionType):
        notReq = ["added_photos", "tagged_in_photo",
                  "approved_friend", "created_group", "created_event"]
        message = []
        BdayMsg = False
        status_type = ""
        Postmsg = ""
        story = ""
        link = ""
        description = ""
        picture = post['id']
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
            message = ["post", "Bday", interactionType, story, Postmsg,
                       description, link, picture, video, date]
        else:
            message = ["post", status_type, interactionType, story,
                       Postmsg, description, link, picture, video, date]
        # print message

        return message

    def addMsg(self, message, interactions):
        if ('data' not in interactions.keys()):
            interactions['data'] = [message]
        else:
            interactions['data'].append(message)

    def createJson(self, doc, interactions, message, nodes, links, linkIndex, access_token, db):
        fb = "https://graph.facebook.com/v2.9/"
        image = ""
        date = ""

        events = db['events']
        feeds = db['feeds']

        self.add_photo_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_likes_small_photo_id_action', 'large_likes_small_action', 2)
        self.add_photo_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_likes_large_photo_id_action', 'small_likes_large_action', 2)
        self.add_photo_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_likes_small_photo_id_timeline', 'large_likes_small_timeline', 2)
        self.add_photo_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_likes_large_photo_id_timeline', 'small_likes_large_timeline', 2)
        self.add_photo_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_comments_on_small_photo_id_action', 'large_comments_on_small_action', 3)
        self.add_photo_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_comments_on_large_photo_id_action', 'small_comments_on_large_action', 3)
        self.add_photo_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_comments_on_small_photo_id_timeline', 'large_comments_on_small_timeline', 3)
        self.add_photo_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_comments_on_large_photo_id_timeline', 'small_comments_on_large_timeline', 3)
        self.add_photo_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_is_tagged_in_small_photo_id_action', 'large_tagged_in_small_action', 4)
        self.add_photo_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_is_tagged_in_large_photo_id_action', 'small_tagged_in_large_action', 4)
        self.add_photo_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_is_tagged_in_small_photo_id_timeline', 'large_tagged_in_small_timeline', 4)
        self.add_photo_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_is_tagged_in_small_photo_id_timeline', 'small_tagged_in_large_timeline', 4)
        self.add_photo_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'co_like_photo_id', 'CoLike', 1)
        self.add_photo_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'co_comment_photo_id', 'CoCommented', 2)
        self.add_photo_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'co_tagged_photo_id', 'CoTagged', 5)

        # POSTS
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_likes_small_post_id_action', 'large_likes_small_action', 2)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_likes_large_post_id_action', 'small_likes_large_action', 2)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_likes_small_post_id_timeline', 'large_likes_small_timeline', 2)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_likes_large_post_id_timeline', 'small_likes_large_timeline', 2)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_comments_on_small_post_id_action', 'large_comments_on_small_post_id_action', 3)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_comments_on_large_post_id_action', 'small_comments_on_large_action', 3)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_comments_on_small_post_id_timeline', 'large_comments_on_small_timeline', 3)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_comments_on_large_post_id_timeline', 'small_comments_on_large_timeline', 3)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_is_tagged_in_small_post_id_action', 'large_tagged_in_small_action', 4)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_is_tagged_in_large_post_id_action', 'small_tagged_in_large_action', 4)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_is_tagged_in_small_post_id_timeline', 'large_tagged_in_small_timeline', 4)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_is_tagged_in_large_post_id_timeline', 'small_tagged_in_large_timeline', 4)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'co_like_post_id', 'CoLike', 1)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'co_comment_post_id', 'CoCommented', 2)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'co_tagged_post_id', 'CoTagged', 5)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_posts_post_to_small_timeline_id', 'large_posts_to_small', 5)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_posts_post_to_large_timeline_id', 'small_posts_to_large', 5)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_posts_photo_video_to_large_timeline_id', 'small_posts_to_large', 5)
        self.add_post_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_posts_photo_video_to_small_timeline_id', 'large_posts_to_small', 5)

        # [Peter, 6/2/17] I think this is all duplication of posts...
        # It's all the same, but there are more classifications under posts.
        # STATUSES
        self.add_status_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_likes_small_status_id_action', 'large_likes_small_action', 2)
        self.add_status_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_likes_large_status_id_action', 'small_likes_large_action', 2)
        self.add_status_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_likes_small_status_id_timeline', 'large_likes_small_timeline', 2)
        self.add_status_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_likes_large_status_id_timeline', 'small_likes_large_timeline', 2)
        self.add_status_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_comments_on_small_status_id_action', 'large_comments_on_small_action', 3)
        self.add_status_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_comments_on_large_status_id_action', 'small_comments_on_large_action', 3)
        self.add_status_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_comments_on_small_status_id_timeline', 'large_comments_on_small_timeline', 3)
        self.add_status_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_comments_on_large_status_id_timeline', 'small_comments_on_large_timeline', 3)
        self.add_status_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_is_tagged_in_small_status_id_action', 'large_tagged_in_small_action', 4)
        self.add_status_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_is_tagged_in_large_status_id_action', 'small_tagged_in_large_action', 4)
        self.add_status_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'large_is_tagged_in_small_status_id_timeline', 'large_tagged_in_small_timeline', 4)
        self.add_status_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'small_is_tagged_in_large_status_id_timeline', 'small_tagged_in_large_timeline', 4)
        self.add_status_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'co_like_status_id', 'CoLike', 1)
        self.add_status_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'co_comment_status_id', 'CoCommented', 2)                  
        self.add_status_message(doc, interactions, nodes, links, linkIndex, access_token, feeds, 'co_tagged_status_id', 'CoTagged', 5)

        # EVENTS
        if ('co_attended_event_id' in doc):
            if (doc['co_attended_event_id'] != [] and doc['co_attended_event_id'] != "NA"):
                for event in doc['co_attended_event_id']:
                    try:
                        cover = description = date = ""
                        eventId = event['id']

                        # grab necessary information from database
                        eventData = events.find_one({'id': eventId}, {'_id': False})
                        name = eventData['name']
                        date = dateparser.parse(eventData['start_time']).strftime('%m/%d/%y')
                        if 'description' in eventData:
                            description = eventData['description']
                        if 'cover' in eventData:
                            cover = eventData['cover']['source']

                        message = ["event", name, description, cover, date]
                        self.addMsg(message, interactions)

                    except Exception, e:
                        print "** EXCEPTION:"
                        print doc['large_name'] + "," + doc['small_name']
                        print "event"
                        print str(e)
                        print eventId
                    self.add_to_link(
                        doc['large_name'], doc['small_name'], 2, nodes, links, linkIndex)

        #Books and Music
        if ('co_like_id' in doc):
            if(doc['co_like_id'] != [] and doc['co_like_id'] != "NA"):
                for x in doc['co_like_id']:
                    try:
                        Id = x['id']
                        about = name = pic = description = ""
                        # fields = "?fields=about,name,picture,description,category"
                        # url = fb + Id + fields + "&access_token=" + access_token
                        # Data = requests.get(url).json()
                        # if('about' in Data):
                        #     about = Data["about"]
                        # if ('name' in Data):
                        #     name = Data['name']
                        # if ('picture' in Data):
                        #     pic = Data['picture']['data']['url']
                        # if ("description" in Data):
                        #     description = Data["description"]
                        # if ("book" in Data['category'] or "Book" in Data['category']):
                        #     message = ["book", about, description, name, pic]
                        # if ("music" in Data['category'] or "Music" in Data['category']):
                        #     message = ["music", about, description, name, pic]
                        self.addMsg(message, interactions)

                    except:
                        print "** EXCEPTION:"
                        print doc['large_name'] + "," + doc['small_name']
                        print "co-likes"
                        print Id
                    self.add_to_link(
                        doc['large_name'], doc['small_name'], 1, nodes, links, linkIndex)

        if ('data' in interactions):
            interactions['data'].sort()
            interactions['data'] = list(
                interactions['data'] for interactions['data'], _ in itertools.groupby(interactions['data']))

    # long_id : long descriptor for interaction
    # short_id : short descriptor for interaction
    # link_number : [Peter] Honestly I'm not sure what it is, but it's different for different things
    def add_photo_message(self, doc, interactions, nodes, links, linkIndex, access_token, feeds, long_id, short_id, link_number):
        fb = "https://graph.facebook.com/v2.9/"
        image = ""
        date = ""

        if (long_id in doc):
            if (doc[long_id] != [] and doc[long_id] != "NA"):
                for photo in doc[long_id]:
                    try:
                        photoId = photo['id']
                        
                        # grab necessary information from database
                        date = feeds.find_one({'id': photoId}, {'_id': False, 'created_time': True})
                        date = dateparser.parse(date['created_time']).strftime('%m/%d/%y')
                        image = photoId

                        message = [
                            "photo", short_id, image, date]
                        # print message
                        self.addMsg(message, interactions)

                    except Exception, e:
                        print "** EXCEPTION:"
                        print doc['large_name'] + "," + doc['small_name']
                        print long_id
                        print str(e)
                        print photoId
                    self.add_to_link(
                        doc['large_name'], doc['small_name'], 2, nodes, links, linkIndex)

    # long_id : long descriptor for interaction
    # short_id : short descriptor for interaction
    # link_number : [Peter] Honestly I'm not sure what it is, but it's different for different things
    # Note[Peter, 6/2/17]: This is quite similar to add_photo_message,
    # but there are a few key differences (the url and how messages are constructed)
    # so I'm keeping them separate for now.
    def add_post_message(self, doc, interactions, nodes, links, linkIndex, access_token, feeds, long_id, short_id, link_number):
        fb = "https://graph.facebook.com/v2.9/"
        # image = ""

        if (long_id in doc):
            if (doc[long_id] != [] and doc[long_id] != "NA"):
                for post in doc[long_id]:
                    try:
                        postId = post['id']

                        # grab necessary information from database
                        postData = feeds.find_one({'id': postId}, {'_id': False})

                        message = self.createPostsMessage(
                            postData, short_id)
                        self.addMsg(message, interactions)

                    except Exception, e:
                        print "** EXCEPTION:"
                        print doc['large_name'] + "," + doc['small_name']
                        print long_id
                        print str(e)
                        print postId
                    self.add_to_link(
                        doc['large_name'], doc['small_name'], link_number, nodes, links, linkIndex)

    # [Peter, 6/2/17] This is almost the exact same as add_post_message... and I don't think statuses
    # are necessary.
    # long_id : long descriptor for interaction
    # short_id : short descriptor for interaction
    # link_number : [Peter] Honestly I'm not sure what it is, but it's different for different things
    def add_status_message(self, doc, interactions, nodes, links, linkIndex, access_token, feeds, long_id, short_id, link_number):
        fb = "https://graph.facebook.com/v2.9/"
        # image = ""

        if (long_id in doc):
            if (doc[long_id] != [] and doc[long_id] != "NA"):
                for status in doc[long_id]:
                    try:
                        statusId = status['id']

                        # grab necessary information from database
                        statusData = feeds.find_one({'id': statusId}, {'_id': False})

                        message = self.createPostsMessage(
                            statusData, short_id)
                        self.addMsg(message, interactions)

                    except Exception, e:
                        print doc['large_name'] + "," + doc['small_name']
                        print long_id
                        print str(e)
                        print statusId
                    self.add_to_link(
                        doc['large_name'], doc['small_name'], link_number, nodes, links, linkIndex)
