# -*- coding: utf-8 -*-
import pymongo
import random
from pymongo import MongoClient

def main():
	client = MongoClient('localhost', 27017)
	db = client.fb_nonuse_Oct_22
	# Create collections
	user = db.user
	taggable_friends = db.taggable_friends
	ego_ego = db.ego_ego
	ego_alter = db.ego_alter
	alter_alter = db.alter_alter
	interactions = db.interactions

	# ego_ego
	ego_ego_list = []
	for u in user.find():
		for v in user.find():
			if u['id'] != v['id']:
				if u['name'] <= v['name']:
					ego_ego_in = interactions.find_one({"$and":[{"small_id":u['id']},{"large_id":v['id']}]})
					if (ego_ego_in != None and ego_ego_in not in ego_ego_list):
						ego_ego_list.append(ego_ego_in)
				else:
					ego_ego_in = interactions.find_one({"$and":[{"small_id":v['id']},{"large_id":u['id']}]})
					if (ego_ego_in != None and ego_ego_in not in ego_ego_list):
						ego_ego_list.append(ego_ego_in)
	for item in ego_ego_list:
		if ego_ego.find_one({"$and":[{"small_id":item['small_id']},{"large_id":item['large_id']}]}) == None:
			ego_ego.insert(item)
		else:
			ego_ego.update({"$and":[{"small_id":item['small_id']},{"large_id":item['large_id']}]},item) 
	# if len(ego_ego_list) == 1:
	# 	ego_ego.insert(ego_ego_list[0])
	# elif len(ego_ego_list) >= 2:
	# 	ego_ego.insert_many(ego_ego_list)
	print ego_ego.count()
	print "Get all ego-ego interactions"

	# ego_alter
	for u in user.find():
		ego_alter_list = []
		print "first line in ego_alter"

		inter_list = interactions.find({"$or":[{"small_id":u['id']},{"large_id":u['id']}]})
		for m in inter_list:
			ego_name = u['name']
			if m['small_name'] == ego_name:
				alter_name = m['large_name']
			else:
				alter_name = m['small_name']

			if user.find_one({"name":alter_name}) != None:
				continue

			check = taggable_friends.find({"$and":[{"name":alter_name},{"friend_of.name":ego_name}]}).count()
			if check > 1:
				continue
			elif check == 0:
				m['friended'] = 0
			elif check == 1:
				m['friended'] = 1
			
			ego_alter_list.append(m)

		print "ego_alter length: {} from {}".format(len(ego_alter_list),u['name'])

		if len(ego_alter_list) > 500:
			ego_alter_list = random.sample(ego_alter_list,500)
	
		for item in ego_alter_list:
			if ego_alter.find_one({"$and":[{"small_id":item['small_id']},{"large_id":item['large_id']}]}) == None:
				ego_alter.insert(item)
			else:
				ego_alter.update({"$and":[{"small_id":item['small_id']},{"large_id":item['large_id']}]},item)

	print ego_alter.count()
	print "Get all ego-alter interactions"

	# alter_alter
	for u in user.find():
		print u
		alter_alter_list = []
		for m in interactions.find({"$and":[{"collected_from.id":u['id']},{"small_id":{"$ne":u['id']}},{"large_id":{"$ne":u['id']}}]}):
			alter_alter_list.append(m)
		print len(alter_alter_list)

		if len(alter_alter_list) > 500:
			alter_alter_list = random.sample(alter_alter_list,500)

		for item in alter_alter_list:
			if alter_alter.find_one({"$and":[{"small_id":item['small_id']},{"large_id":item['large_id']}]}) == None:
				alter_alter.insert(item)
			else:
				alter_alter.update({"$and":[{"small_id":item['small_id']},{"large_id":item['large_id']}]},item)
		
		print "Get {}\'s alter-alter interactions".format(u['name'])

	print alter_alter.count()
	print "Get all alter-alter interactions"

if __name__ == "__main__":
	main()
