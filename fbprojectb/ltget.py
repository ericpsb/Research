#!/usr/bin/env python
# -*- coding: utf-8 -*-
import httplib
import json
from pymongo import MongoClient
# import logging
import config
import sys
import datetime
import update_db_v4
import os

def main():
    if not check_args():
        print 'Access token required.'
        quit()

    # get short term access token
    short_term_access_token = sys.argv[1]

    # logging.basicConfig(filename='ltget_log.txt',
    #                     format='%(asctime)s %(message)s', level=logging.DEBUG)
    # logging.info("=================== Start ===================")

    # Storing app id and secret
    appid = "1582658458614337"
    appsecret = "c938c071248be2751bbde872cdc56262"

    # Connecting to MongoDB
    client = MongoClient(config.get_connection_string())
    db = client[config.USER_DB]
    collection = db['fb-users']

    try:
        # build httpconnection object
        conn = httplib.HTTPSConnection('graph.facebook.com')

        # setting up GET request
        conn.request("GET", "/oauth/access_token?grant_type=fb_exchange_token&client_id=" +
                        appid + "&client_secret=" + appsecret + "&fb_exchange_token=" + short_term_access_token + "")

        # getting and storing  the full response
        ltat = conn.getresponse()
        data = json.load(ltat)
        acltat = data['access_token']

        # #Creating a document to store in a mongoDb collection
        userInfo = {}
        # #Storing valuable information from the facebook graph:
        userInfo['access_token'] = acltat
        userInfo['token_date'] = datetime.datetime.utcnow()
        userInfo['processing'] = True
        
        conn.request("GET", "/v2.10/me?fields=name,id,first_name,last_name,gender,email,birthday&access_token=" + acltat)
        resp = conn.getresponse()
        profile = json.load(resp)
        print profile

        # profile = graph.get('me')
        user_name = profile['name']
        user_id = profile['id']
        existing = collection.find_one({"user id": user_id})

        if existing is None:
            userInfo['first_name'] = profile['first_name']
            userInfo['last_name'] = profile['last_name']
            userInfo['user id'] = user_id
            userInfo['gender'] = profile['gender']
            userInfo['email'] = profile['email']
            userInfo['birthday'] = profile['birthday']
            userInfo['name'] = user_name.title()
            userInfo['vizDone'] = 0
            print "This user does not exist in the database."
            collection.insert_one(userInfo)
        else:
            # check if this user is already processing
            if 'processing' in existing and existing['processing'] == True:
                print 'User already processing in other thread'
                return

            print "This user exists in the database."
            collection.update({'user id': user_id}, {
                "$set": {'access_token': acltat, 'token_date': datetime.datetime.utcnow(), 'processing': True}})
    except Exception, e:
        print "EXCEPTION: " + str(e)
        print "User logged out."
        os.system("""echo "Hi,\n\nWe're sorry, but something went wrong with your visualization. Please try logging in again at https://das-lab.org/truefriend. Thank you." | mail -a "From: TrueFriend <truefriend@das-lab.org>" -s "TrueFriend - Error" {}""".format(profile['email']))
        return
    
    try:
        update_db_v4.run_update(acltat)
    except Exception as exc:
        print 'Failed during update_db'
        print type(exc).__name__
        print exc.args
        import traceback
        print traceback.format_exc()
        os.system("""echo "Hi,\n\nWe're sorry, but something went wrong with your visualization. Please try logging in again at https://das-lab.org/truefriend. Thank you." | mail -a "From: TrueFriend <truefriend@das-lab.org>" -s "TrueFriend - Error" {}""".format(profile['email']))
        return
    finally:
        # say they're no longer processing
        userInfo['processing'] = False
        collection.update({'user id': user_id}, {"$set": {'processing': False}})

def check_args():
    return len(sys.argv) == 2

if __name__ == "__main__":
    main()
