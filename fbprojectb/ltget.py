# -*- coding: utf-8 -*-
# import stuff here
import httplib
import csv
import facebook
import facepy
import json
import pymongo
from pymongo import MongoClient, HASHED, ASCENDING, DESCENDING
import simplejson as json
import requests
import time
import logging


def main():
    logging.basicConfig(filename='ltget_log.txt',
                        format='%(asctime)s %(message)s', level=logging.DEBUG)
    logging.info("=================== Start ===================")

    # fixing the Insecure platform issue on Facepy
    import urllib3.contrib.pyopenssl

    # reading check file for status. It points to the last line of
    # accesstokens.txt.
    checkfile = open('check.txt', 'r')
    check = int(checkfile.read())
    checkfile.close()

    # need to open accesstokens.txt to read the line denoted by
    actok = open('accesstokens.txt', 'r')
    lines = actok.readlines()
    actok.close()

    # Gets the number of lines from index(from check.txt) to last line in
    # accesstokes.txt
    print len(lines)
    remaining = lines[check:]
    print len(remaining)

    # Storing app id and secret
    appid = "1582658458614337"
    appsecret = "c938c071248be2751bbde872cdc56262"

    # Connecting to MongoDB
    client = MongoClient('localhost', 27017)
    # Creating a MongoDB database
    db = client['fbapp-DB']
    # Creating a collection within the database
    collection = db['fb-users']

    # If no. of lines in remaining is 0, do nothing. If there are accesstokens
    # to be converted do the following
    if len(remaining) != 0:
        # let us traverse the list till the end to get all new access tokens
        for line in remaining:
            check = check + 1

            if line != ",\n":
                try:
                    # The try block helps ignore any missed cases, eg, cases in
                    # which people logged out and their access tokens are not
                    # valid anymore
                    start_time = time.clock()  # record processing time/authorized user
                    print line
                    lsplit = line.split(',')
                    stat = lsplit[0]
                    uid = lsplit[1]

                    # build httpconnection object
                    conn = httplib.HTTPSConnection('graph.facebook.com')

                    # setting up GET request
                    conn.request("GET", "/oauth/access_token?grant_type=fb_exchange_token&client_id=" +
                                 appid + "&client_secret=" + appsecret + "&fb_exchange_token=" + stat + "")

                    # getting and storing  the full response
                    ltat = conn.getresponse()
                    data = ltat.read()
                    print data

                    # first split the response string along '='
                    fsplit = data.split('=')

                    filelt = open('longtermaccesstoken.txt', 'a')
                    # second split string along & (all this because accesstoken
                    # size could be variable)
                    ssplit = fsplit[1].split('&')

                    # finally store the result of second split into long term
                    # access token
                    acltat = ssplit[0]

                    # we need to store this into a file of long term
                    # accesstokens
                    thisrow = [1, 2]
                    thisrow[0] = acltat
                    thisrow[1] = uid
                    writer = csv.writer(filelt, delimiter=',')

                    filelt.write(acltat + ',' + uid + '\n')
                    filelt.close()

                    # #Creating a document to store in a mongoDb collection
                    userInfo = {}
                    # #Storing valuable information from the facebook graph:
                    userInfo['access_token'] = acltat
                    graph = facepy.GraphAPI(acltat)
                    profile = graph.get('me')
                    user_name = profile['name']
                    user_id = profile['id']
                    existing = collection.find_one({"user id": user_id})
                    if existing == None:
                        userInfo['first_name'] = profile['first_name']
                        userInfo['last_name'] = profile['last_name']
                        userInfo['user id'] = user_id
                        userInfo['gender'] = profile['gender']
                        userInfo['email'] = profile['email']
                        userInfo['birthday'] = profile['birthday']
                        userInfo['name'] = user_name.title()
                        userInfo['vizDone'] = 0
                        print "YOLO, this user does not exit in the database"
#                                        print "new profile",userInfo
#					print "old profle",existing
                        collection.insert_one(userInfo)
                    else:
                        #					print "current profile",existing
                        #					print "new profile",userInfo
                        print "this user exists in the database"
                        collection.update({'user id': user_id}, {
                                          "$set": {'access_token': acltat}})

                    # need to increment the value of check by 1
#	                        check = check + 1

                    # open check.txt and store the updated value of check in
                    # it.
                    checkfileagain = open('check.txt', 'w')
                    checkfileagain.write(str(check))
                    checkfileagain.close()
                except:
                    print "user loged out"
                    # need to increment the value of check by 1
 #                               check = check + 1

                    # open check.txt and store the updated value of check in
                    # it.
                    checkfileagain = open('check.txt', 'w')
                    checkfileagain.write(str(check))
                    checkfileagain.close()


if __name__ == "__main__":
    main()
