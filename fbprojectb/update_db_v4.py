# -*- coding: utf-8 -*-
import httplib
import csv
import json
import pymongo
from pymongo import MongoClient, HASHED, ASCENDING, DESCENDING
from query import get_interaction
import simplejson as json
import requests
import time
import logging
import newViz
#from subprocess import Popen, PIPE
import os
import config
import sys

def run_update(access_token):
    logging.basicConfig(filename='update_db_log.txt',
                        format='%(asctime)s %(message)s', level=logging.DEBUG)
    logging.info("=================== Start ===================")

    # reading check file for status. It points to the last line of
    # longtermaccesstokens.txt in previous run.
    # with open('check_db.txt', 'r') as fileone:
    #     check = int(fileone.read())
    #     logging.info("Read check_db.txt")
    #     print "Read check"

    # with open('longtermaccesstoken.txt') as filetwo:
    #     lines = filetwo.readlines()
    #     logging.info("Read longtermaccesstoken.txt")
    #     print "Read longtermaccesstoken"

    # # if we have new users logged in:
    # if (check < len(lines)):
    #     remaining = lines[check:]
    #     logging.info(
    #         "Number of new users: {}. Including blank lines".format(len(remaining)))
    #     print len(remaining)

    runtime = []

    # Connecting to MongoDB
    client = MongoClient(config.get_connection_string())
    db = client[config.FB_INFO_DB]
    # Create or use collections
    user = db.user
    people = db.people  # everyone appeared in comments, tags, likes, etc
    events = db.events
    friends = db.friends
    mutual = db.mutual
    taggable_friends = db.taggable_friends  # taggable friends
    likes = db.likes
    feeds = db.feeds
    interactions = db.interactions
    logging.info("Connected to MongoDB")

    # initialize the fields
    fb = 'https://graph.facebook.com/v2.9/me?fields='
    me_field = 'id,name,first_name,last_name,email,gender,link,verified,timezone,updated_time,birthday'
    event_field = 'events.limit(50){name,description,start_time,id,rsvp_status,end_time,category,cover,owner,type,attending.limit(50)}'
    friend_field = 'friends.limit(50){name,id,context}'
    taggable_friend_field = 'taggable_friends.limit(100)'
    like_field = 'likes.limit(100){name,category,id,description}'
    feed_field = 'feed.limit(50){created_time,from,message,link,message_tags,source,status_type,story,story_tags,type,comments.limit(100){created_time,message,from},likes.limit(100){id,name},with_tags.limit(100)}'
    me_url = fb + me_field + '&access_token='
    activity_field = event_field + ',' + friend_field + ',' + \
        taggable_friend_field + ',' + like_field + ',' + feed_field
    activity_url = fb + activity_field + '&access_token='

    # traverse the token list till the end to get all new access tokens
    # for line in remaining:

    to_update_friends = []  # alter id list

    start_time = time.clock()  # record processing time/authorized user

    # check = check + 1

    # token = line.split(',')[0]
    token = access_token

    # empty line in longtermaccesstoken.txt
    # if (token == '\n'):
    #     with open('check_db.txt', 'w') as filetemp:
    #         filetemp.write(str(check))
    #         logging.info(
    #             "check_db.txt is updated for empty line. Now after line {}".format(check))
    #     continue

    url = me_url + token
    profile = requests.get(url).json()

    # expired access token
    # if ('error' in profile):
    #     print "Error in access tokens:", token
    #     print profile
    #     logging.info("Error in the access token: {}".format(token))
    #     logging.info(profile)

    #     with open('check_db.txt', 'w') as filetemp:
    #         filetemp.write(str(check))
    #         logging.info(
    #             "check_db.txt is updated for an error in access token. Now after line {}".format(check))
    #     continue

    # valid token
    profile['name'] = profile['name'].title()
    profile['access_token'] = token
    logging.info("Get a new user's profile: {}".format(profile))

    user_name = profile['name']
    user_id = profile['id']

    # check if the user exsits in db
    existing = user.find_one({"id": user_id})
    if existing == None:
        user.insert_one(profile)
        logging.info(
            "Inserted new user {} into User".format(user_name))
    else:
        user.update({'id': user_id}, profile)
        logging.info("Updated {}\'s profile".format(user_name))

    # get this user's timeline data and store in database
    update_db(token, activity_url, profile, user_name, user_id, user, people, events,
                friends, mutual, taggable_friends, likes, feeds, interactions, to_update_friends)

    # Set up indexes if this is the first user
    if user.find().count() == 1:
        user.create_index([("name", ASCENDING)])
        user.create_index([("id", ASCENDING)])

        people.create_index([("id", ASCENDING)])
        people.create_index([("collected_from.id", ASCENDING)])

        events.create_index([("id", ASCENDING)])
        events.create_index([("attended_by.id", ASCENDING)])
        events.create_index([("attending.data.id", ASCENDING)])

        likes.create_index([("id", ASCENDING)])
        likes.create_index([("liked_by.id", ASCENDING)])

        friends.create_index([("friend_of.id", ASCENDING)])
        friends.create_index([("id", ASCENDING)])

        mutual.create_index([("friend_of.id", ASCENDING)])
        mutual.create_index([("id", ASCENDING)])

        taggable_friends.create_index(
            [("friend_of.id", ASCENDING), ("name", DESCENDING)])

        feeds.create_index([("id", ASCENDING)])
        feeds.create_index([("type", ASCENDING)])
        feeds.create_index([("collected_from.id", ASCENDING)])
        feeds.create_index([("from.id", ASCENDING)])
        feeds.create_index([("with_tags.data.id", ASCENDING)])
        feeds.create_index([("story_tags.data.id", ASCENDING)])
        feeds.create_index([("status_type", ASCENDING)])
        feeds.create_index([("likes.data.id", ASCENDING)])
        feeds.create_index([("comments.data.from.id", ASCENDING)])

        interactions.create_index([("large_id", ASCENDING)])
        interactions.create_index([("small_id", ASCENDING)])
        interactions.create_index([("collected_from.id", ASCENDING)])
        interactions.create_index([("collected_from.name", ASCENDING)])
        interactions.create_index([("large_name", ASCENDING)])
        interactions.create_index([("small_name", ASCENDING)])
        logging.info("Created indices for interactions")

        print "Created indices"
        logging.info("Created indices")

    difference = time.clock() - start_time
    runtime.append(difference)
    logging.info("Processing {}\'s timeline took {} CPU time".format(
        user_name, difference))

    # with open('check_db.txt', 'w') as filetwo:
    #     filetwo.write(str(check))
    #     logging.info(
    #         "check_db.txt is updated for successfully collecting a user's data.")

    # close database connections - newViz will use its own
    client.close()

    # generate or update visualization
    to_update_friends = list(set(to_update_friends))
    x = newViz.GenerateViz()
    x.init(user_id)
    logging.info("Generated or updated visualization")
    #Popen(['mail','-s','Your visualization is ready to view',profile['email'],'<<<','Hi,Your network visualization on the Social Interaction Graph app is ready to view. Thank you for your support!'])
    vizurl = "https://das-lab.org/truefriend/viz.php?resp={}&user={}".format(
        token, user_id)
    # with open("email_content.txt","a") as myfile:
    # myfile.write("/n"+vizurl)
    os.system(
        """echo "Hi,\n\nYour network visualization on our Facebook App TrueFriends is ready to view now. The link is shown below. Thank you for your support on our project"'!'"\n\n"'{}' | mail -a "From: TrueFriend <truefriend@das-lab.org>" -s "Your network visualization is ready" {}""".format(vizurl, profile['email']))
    # with open('check_db.txt', 'w+') as file2:
    #lines = file2.readlines()
    #lines = lines[:-1]
    # file2.write(lines)
    for friend in to_update_friends:
        y = newViz.GenerateViz()
        y.init(friend)
        logging.info("Updated visualization for a friend")

    print 'Past processing time: {}'.format(runtime)
    logging.info('Past processing time: {}'.format(runtime))
    # no new user
    # else:
    #     logging.info("No new user.")

#===========================================


def update_db(token, activity_url, profile, user_name, user_id, user, people, events, friends, mutual, taggable_friends, likes, feeds, interactions, to_update_friends):
    activity_total_url = activity_url + token

    activities = requests.get(activity_total_url).json()
    print 'Fetched {}\'s timeline data'.format(user_name)
    print "timeline keys: ", activities.keys()
    logging.info("Fetched {}\'s timeline data".format(user_name))

    if 'error' in activities:
        logging.info("Error in getting {}\'s timeline data: {}".format(
            user_name, activities))

    if 'events' in activities:
        pre_process('events', events, activities,
                    user_name, user_id, 'attended_by')

    if 'likes' in activities:
        pre_process('likes', likes, activities, user_name, user_id, 'liked_by')

    if 'friends' in activities:
        profile['total_friends'] = activities['friends']['summary']['total_count']
        user.update({"id": profile['id']}, profile)

        friends_list = pagination(activities['friends'])

        for friend in friends_list:
            person = {}
            person['id'] = friend['id']
            person['name'] = friend['name']
            person['friend_of'] = [{"name": user_name, "id": user_id}]

            if friends.find_one({"id": person['id']}) == None:
                friends.insert_one(person)
            else:
                friends.update({"id": person['id']}, {"$addToSet": {
                               "friend_of": {"name": user_name, "id": user_id}}})
                person['mutual_friends'] = friend['context']['mutual_friends']['summary']['total_count'] if 'mutual_friends' in friend['context'] else 0
                person['mutual_likes'] = friend['context']['mutual_likes']['summary']['total_count']

                if mutual.find_one({"$and": [{"id": person['id']}, {"friend_of.id": user_id}]}) == None:
                    mutual.insert_one(person)
                else:
                    mutual.update(
                        {"$and": [{"id": person['id']}, {"friend_of.id": user_id}]}, person)

                if user.find_one({"id": person['id']}) != None:
                    to_update_friends.append(person['id'])

            print "Store all friends data from {}".format(user_name)
            logging.info("Store all friends data from {}".format(user_name))

    if 'taggable_friends' in activities:
        taggable_list = pagination(activities['taggable_friends'])
        for taggable in taggable_list:
            taggable['friend_of'] = [{"name": user_name, "id": user_id}]
            if taggable_friends.find_one({"$and": [{"name": taggable['name']}, {"friend_of.id": user_id}]}) == None:
                taggable_friends.insert_one(taggable)

        print "Store all taggable friends from {}".format(user_name)
        logging.info("Store all taggable friends from {}".format(user_name))

    track_list = []
    if 'feed' in activities:
        process_feed(feeds, activities, user_name, user_id, 'collected_from', people,
                     interactions, user, events, friends, mutual, taggable_friends, likes, track_list)

    print 'All of user {}\'s data are processed'.format(user_name)
    logging.info("All of user {}\'s data are processed".format(user_name))


# A function to loop through pagination and insert document into corresponding collection
# Apply to feed
# def process(item, people, track_list, interactions, user_name, user_id, user, events, friends, mutual, taggable_friends,
#             likes, feeds):

def process_feed(feeds, data, user_name, user_id, relation, people, interactions, user, events, friends, mutual, taggable_friends, likes, track_list):
    print "                                  Working on feed's pagination"
    logging.info(
        "                                 Working on feed's pagination")
    result_total = pagination(data['feed'])
    print 'Find {}\'s {}'.format(user_name, 'feed')
    logging.info("Find {}\'s {}".format(user_name, 'feed'))

    for doc in result_total:
        sys.stdout.flush()
        # pagination on tags/likes/comments
        if 'likes' in doc:
            doc['likes']['data'] = pagination(doc['likes'])
        if 'comments' in doc:
            doc['comments']['data'] = pagination(doc['comments'])
        if 'with_tags' in doc:
            doc['with_tags']['data'] = pagination(doc['with_tags'])

        # check the document if exists in the feeds
        doc_in_col = feeds.find_one({"id": doc['id']})
        # if it not exists in relevant feeds
        if doc_in_col == None:
            # add "relation" attribute to record source and insert into feeds
            doc[relation] = [{"name": user_name, "id": user_id}]
            feeds.insert_one(doc)
        # Otherwise, update the existing one
        else:
            doc[relation] = doc_in_col[relation]
            if {"name": user_name, "id": user_id} not in doc[relation]:
                doc[relation].append({"name": user_name, "id": user_id})
            feeds.update({"id": doc['id']}, doc)

    for doc in result_total:
        sys.stdout.flush()
        # collect people name and id from a doc, add to both people feeds
        people_list = []
        find_people(doc, people, people_list, user_name, user_id)
        people_set = set(people_list)
        people_list = sorted(list(people_set))

        # pair wise interactions
        for A in people_list:
            for B in people_list:
                if A != B:

                    if people.find_one({"id": A})['name'] <= people.find_one({"id": B})['name']:
                        small = {"name": people.find_one(
                            {"id": A})['name'], "id": A}
                        large = {"name": people.find_one(
                            {"id": B})['name'], "id": B}
                    else:
                        small = {"name": people.find_one(
                            {"id": B})['name'], "id": B}
                        large = {"name": people.find_one(
                            {"id": A})['name'], "id": A}

                    # compare it to track_list
                    # which tracks node pairs already created from this user
                    track_pair = {
                        "small_id": small['id'], "large_id": large['id']}
                    # if this node pair exists, print information
                    if track_pair in track_list:
                        continue
                    # else, add to the tracking list[]
                    else:
                        track_list.append(track_pair)

                        # get the pair wise interaction for this node pair
                        # def
                        # get_interaction(small,large,user,events,friends,mutual,taggable_friends,likes,feeds):
                        pair = get_interaction(
                            small, large, user, events, friends, mutual, taggable_friends, likes, feeds)
                        existing = interactions.find_one(
                            {"$and": [{"small_id": small['id']}, {"large_id": large['id']}]})

                        # if this node pair does not exists, insert
                        if existing == None:
                            pair['collected_from'] = [
                                {"name": user_name, "id": user_id}]
                            interactions.insert_one(pair)
                        # or update the existing one
                        # remember to copy existing "collected_from" list
                        else:
                            pair['collected_from'] = existing['collected_from']
                            if {"name": user_name, "id": user_id} not in pair['collected_from']:
                                pair['collected_from'].append(
                                    {"name": user_name, "id": user_id})
                            interactions.update(
                                {"$and": [{"small_id": small['id']}, {"large_id": large['id']}]}, pair)

    print '\nStore all {} from {} in the database'.format('feed', user_name)
    logging.info(
        "Store all {} from {} in the database".format('feed', user_name))


# A helper function for function find_people
# Apply to from and comments
def create_person_one(key, doc, collection, people_list, user_name, user_id):
    person = {}
    person['name'] = doc[key]['name'].title()
    person['id'] = doc[key]['id']
    person['collected_from'] = [{"name": user_name, "id": user_id}]

    if collection.find_one({"id": person['id']}) == None:
        collection.insert_one(person)
    else:
        collection.update({"id": person['id']}, {"$addToSet": {
                          "collected_from": {"name": user_name, "id": user_id}}})

    people_list.append(person['id'])


# A helper function for function find_people
# Apply to tags and likes
def create_person_two(doc, collection, people_list, user_name, user_id):
    person = {}
    person['name'] = doc['name'].title()
    person['id'] = doc['id']
    person['collected_from'] = [{"name": user_name, "id": user_id}]

    if collection.find_one({"id": person['id']}) == None:
        collection.insert_one(person)
    else:
        collection.update({"id": person['id']}, {"$addToSet": {
                          "collected_from": {"name": user_name, "id": user_id}}})

    people_list.append(person['id'])


# A function to collect people from feeds
def find_people(doc, collection, people_list, user_name, user_id):
    if 'from' in doc:
        if doc['from']['id'] != None:
            create_person_one('from', doc, collection,
                              people_list, user_name, user_id)
    if 'comments' in doc:
        for comment in doc['comments']['data']:
            if 'from' in comment:
                if comment['from']['id'] != None:
                    create_person_one('from', comment, collection,
                                      people_list, user_name, user_id)
    if 'with_tags' in doc:
        for tag in doc['with_tags']['data']:
            if tag['id'] != None:
                create_person_two(
                    tag, collection, people_list, user_name, user_id)
    if 'likes' in doc:
        for like in doc['likes']['data']:
            if like['id'] != None:
                create_person_two(like, collection,
                                  people_list, user_name, user_id)
    if 'story_tags' in doc:
        for item in doc['story_tags']:
            # for item in doc['story_tags'][key]:
            if (item['id'] != None) and (item['name'] != "") and ('type' in item):
                if (item['type'] == 'user') and (item['id'] != user_id):
                    create_person_two(item, collection,
                                      people_list, user_name, user_id)
    logging.info("Collected everyone for this item")


# A function to loop through pagination and update likes/comments/tags
# and other list type data
# data parameter: if 'likes' has keys 'paging' and 'data', the parameter
# should be 'likes'
def pagination(data):
    result_total = []
    try:
        while (data['data'] != []):
            result_total.extend(data['data'])
            if 'paging' in data:
                if 'next' in data['paging']:
                    next_url = data['paging']['next']
                    data = requests.get(next_url).json()
                else:
                    break
            else:
                break
    except KeyError:
        pass
    return result_total

# A function to loop through pagination and insert document into correpsonding collection
# Apply to events, friends, likes


def pre_process(key, collection, data, user_name, user_id, relation):
    print "                                  Working on {} pagination".format(key)
    logging.info(
        "                                  Working on {} pagination".format(key))
    result_total = pagination(data[key])
    print 'Find {}\'s {}'.format(user_name, key)
    logging.info("Find {}\'s {}".format(user_name, key))

    # for an activity record:
    for doc in result_total:
        existing = collection.find_one({"id": doc['id']})
        # if it not exists in relevant collection
        if existing == None:
            # add "relation" attribute to record source
            doc[relation] = [{"name": user_name, "id": user_id}]
            # insert into collection
            collection.insert_one(doc)
        # Otherwise, update the existing one's "relation" attribute
        else:
            doc[relation] = existing[relation]
            if {"name": user_name, "id": user_id} not in doc[relation]:
                doc[relation].append({"name": user_name, "id": user_id})
            collection.update({"id": doc['id']}, doc)
    print 'Store all {} from {} in the database'.format(key, user_name)
    logging.info("Store all {} from {} in the database".format(key, user_name))
