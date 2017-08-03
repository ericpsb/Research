# -*- coding: utf-8 -*-
import csv
import pymongo
import random
from pymongo import MongoClient
import logging
	
def main():
	logging.basicConfig(filename='output_log.txt',format='%(asctime)s %(message)s',level=logging.DEBUG)
	logging.info("=================== Start ===================")

	# Connect MongoDB
	client = MongoClient() #default to localhost, port 27017
	db = client.fb_nonuse_Oct_22
	user = db.user
	interactions = db.interactions
	ego_ego = db.ego_ego
	ego_alter = db.ego_alter
	alter_alter = db.alter_alter
	print 'Connected to MongoDB'
	logging.info("Connected to MongoDB")

	example = interactions.find_one()
	field_names = []
	for key in example:
		if key != "large_friends" and key != "small_friends":
			if type(example[key]) == int:
				field_names.append(key)

	names = ["small_id","small_name","large_id","large_name","friended"]
	field_names.extend(names)
	logging.info("Get field names")

	with open('ego_alter.csv','w') as file:
		writer = csv.DictWriter(file,fieldnames = field_names,extrasaction='ignore')
		writer.writeheader()
		for e in ego_alter.find():
			try:
				writer.writerow(e)
			except UnicodeEncodeError:
				e['small_name'] = e['small_name'].encode('utf-8')
				e['large_name'] = e['large_name'].encode('utf-8')
				writer.writerow(e)
		print "Get ego alter interactions"
		logging.info("Write out ego alter interactions")

	with open('alter_alter.csv','w') as file:
		writer = csv.DictWriter(file,fieldnames = field_names,extrasaction='ignore')
		writer.writeheader()
		for e in alter_alter.find():
			try:
				writer.writerow(e)
			except UnicodeEncodeError:
				e['small_name'] = e['small_name'].encode('utf-8')
				e['large_name'] = e['large_name'].encode('utf-8')
				writer.writerow(e)
		print "Get alter alter interactions"
		logging.info("Write out alter alter interactions")
	
	second = ["co_friend_count","co_friend_count_app","co_like_count","large_friends","small_friends"]
	field_names.extend(second)

	with open('ego_ego.csv','w') as file:
		writer = csv.DictWriter(file,fieldnames = field_names,extrasaction='ignore')
		writer.writeheader()
		for e in ego_ego.find():
			try:
				writer.writerow(e)
			except UnicodeEncodeError:
				e['small_name'] = e['small_name'].encode('utf-8')
				e['large_name'] = e['large_name'].encode('utf-8')
				writer.writerow(e)
		print "Get ego ego interactions"
		logging.info("Write out ego ego interactions")

	logging.info("=================== End ===================")

if __name__ == "__main__":
	main()
