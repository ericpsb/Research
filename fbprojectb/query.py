import logging

def get_interaction(small,large,user,events,friends,mutual,taggable_friends,likes,feeds):
	pair = {}
	pair['small_name'] = small['name']
	pair['small_id'] = small['id']
	pair['large_name'] = large['name']
	pair['large_id'] = large['id']

	# if two nodes are both users, we have data on events, mutual friends and mutual likes
	if (user.find_one({"id":small['id']}) != None) and (user.find_one({"id":large['id']}) != None):
		# co-like
		co_like_id = []
		for m in likes.find({"$and":[{"liked_by.id":small['id']},{"liked_by.id":large['id']}]},{"id":1,"_id":0}):
			co_like_id.append(m)
		co_like_count = len(co_like_id)
		
		# co-friend
		co_friend_id_app = []
		for m in friends.find({"$and":[{"friend_of.id":small['id']},{"friend_of.id":large['id']}]},{"id":1,"_id":0}):
			co_friend_id_app.append(m)
		co_friend_count_app = len(co_friend_id_app)
		
		small_mutual = mutual.find_one({"$and":[{"id":small['id']},{"friend_of.id":large['id']}]})
		if small_mutual == None:
			small_mutual = 0
		else:
			small_mutual = small_mutual['mutual_friends']

		large_mutual = mutual.find_one({"$and":[{"id":large['id']},{"friend_of.id":small['id']}]})
		if large_mutual == None:
			large_mutual = 0
		else:
			large_mutual = large_mutual['mutual_friends']
		co_friend_count = max(small_mutual,large_mutual)

		# friended
		if mutual.find_one({"$and":[{"id":small['id']},{"friend_of.id":large['id']}]}) == None:
			small_friended = 0
		else:
			small_friended = 1

		if mutual.find_one({"$and":[{"id":large['id']},{"friend_of.id":small['id']}]}) == None:
			large_friended = 0
		else:
			large_friended = 1

		friended = max(small_friended,large_friended)

	else:
		co_like_id = 'NA'
		co_like_count = 'NA'

		co_friend_id_app = 'NA'
		co_friend_count_app = 'NA'
		co_friend_count = 'NA'
		friended = 'NA'

	pair['friended'] = friended
	
	pair['co_like_id'] = co_like_id
	pair['co_like_count'] = co_like_count
	
	pair['co_friend_id_app'] = co_friend_id_app
	pair['co_friend_count_app'] = co_friend_count_app
	pair['co_friend_count'] = co_friend_count

	# co activity

	# co-attended event
	co_attended_event_id = []
	for m in events.find({"$and":[{"attended_by.id":small['id']},{"attended_by.id":large['id']},{"rsvp_status":'attending'}]},{"id":1,"_id":0}):
		co_attended_event_id.append(m)
	for m in events.find({"$and":[{"attending.data.id":small['id']},{"attending.data.id":large['id']}]},{"id":1,"_id":0}):
		if m not in co_attended_event_id:	
			co_attended_event_id.append(m)	
	co_attended_event_count = len(co_attended_event_id)
	pair['co_attended_event_id'] = co_attended_event_id
	pair['co_attended_event_count'] = co_attended_event_count

	# photo
	co_tagged_photo_id = [] # exclude posted by small or large
	for m in feeds.find({"$and":[{"from.id":{"$ne":small['id']}},{"from.id":{"$ne":large['id']}},{"type":"photo"},{"with_tags.data.id":small['id']},{"with_tags.data.id":large['id']}]},{"id":1,"_id":0}):
		co_tagged_photo_id.append(m)
	for m in feeds.find({"$and":[{"from.id":{"$ne":small['id']}},{"from.id":{"$ne":large['id']}},{"type":"photo"},{"story_tags.data.id":small['id']},{"story_tags.data.id":large['id']}]},{"id":1,"_id":0}):
		if m not in co_tagged_photo_id:
			co_tagged_photo_id.append(m)
	pair['co_tagged_photo_id']= co_tagged_photo_id
	pair['co_tagged_photo_count'] = len(co_tagged_photo_id)

	co_like_photo_id = [] # exclude posted by small or large
	for m in feeds.find({"$and":[{"from.id":{"$ne":small['id']}},{"from.id":{"$ne":large['id']}},{"type":"photo"},{"likes.data.id":small['id']},{"likes.data.id":large['id']}]},{"id":1,"_id":0}):
		co_like_photo_id.append(m)
	pair['co_like_photo_id']= co_like_photo_id
	pair['co_like_photo_count'] = len(co_like_photo_id)

	co_comment_photo_id = [] # exclude posted by small or large
	for m in feeds.find({"$and":[{"from.id":{"$ne":small['id']}},{"from.id":{"$ne":large['id']}},{"type":"photo"},{"comments.data.from.id":small['id']},{"comments.data.from.id":large['id']}]},{"id":1,"_id":0}):
		co_comment_photo_id.append(m)
	pair['co_comment_photo_id']= co_comment_photo_id
	pair['co_comment_photo_count'] = len(co_comment_photo_id)

	# status, include note
	co_tagged_status_id = [] # exclude posted by small or large
	for m in feeds.find({"$and":[{"from.id":{"$ne":small['id']}},{"from.id":{"$ne":large['id']}},{"type":{"$in":["status","note"]}},{"with_tags.data.id":small['id']},{"with_tags.data.id":large['id']}]},{"id":1,"_id":0}):
		co_tagged_status_id.append(m)
	pair['co_tagged_status_id']= co_tagged_status_id
	pair['co_tagged_status_count'] = len(co_tagged_status_id)

	co_like_status_id = [] # exclude posted by small or large
	for m in feeds.find({"$and":[{"from.id":{"$ne":small['id']}},{"from.id":{"$ne":large['id']}},{"type":{"$in":["status","note"]}},{"likes.data.id":small['id']},{"likes.data.id":large['id']}]},{"id":1,"_id":0}):
		co_like_status_id.append(m)
	pair['co_like_status_id']= co_like_status_id
	pair['co_like_status_count'] = len(co_like_status_id)

	co_comment_status_id = [] # exclude posted by small or large
	for m in feeds.find({"$and":[{"from.id":{"$ne":small['id']}},{"from.id":{"$ne":large['id']}},{"type":{"$in":["status","note"]}},{"comments.data.from.id":small['id']},{"comments.data.from.id":large['id']}]},{"id":1,"_id":0}):
		co_comment_status_id.append(m)
	pair['co_comment_status_id']= co_comment_status_id
	pair['co_comment_status_count'] = len(co_comment_status_id)

	# post (link and video)
	co_tagged_post_id = [] # exclude posted by small or large
	for m in feeds.find({"$and":[{"from.id":{"$ne":small['id']}},{"from.id":{"$ne":large['id']}},{"type":{"$in":["link","video"]}},{"with_tags.data.id":small['id']},{"with_tags.data.id":large['id']}]},{"id":1,"_id":0}):
		co_tagged_post_id.append(m)
	pair['co_tagged_post_id']= co_tagged_post_id
	pair['co_tagged_post_count'] = len(co_tagged_post_id)

	co_like_post_id = [] # exclude posted by small or large
	for m in feeds.find({"$and":[{"from.id":{"$ne":small['id']}},{"from.id":{"$ne":large['id']}},{"type":{"$in":["link","video"]}},{"likes.data.id":small['id']},{"likes.data.id":large['id']}]},{"id":1,"_id":0}):
		co_like_post_id.append(m)
	pair['co_like_post_id']= co_like_post_id
	pair['co_like_post_count'] = len(co_like_post_id)

	co_comment_post_id = [] # exclude posted by small or large
	for m in feeds.find({"$and":[{"from.id":{"$ne":small['id']}},{"from.id":{"$ne":large['id']}},{"type":{"$in":["link","video"]}},{"comments.data.from.id":small['id']},{"comments.data.from.id":large['id']}]},{"id":1,"_id":0}):
		co_comment_post_id.append(m)
	pair['co_comment_post_id']= co_comment_post_id
	pair['co_comment_post_count'] = len(co_comment_post_id)
	
	# item ownership: from whose timeline
	# "collected_from"
	# photo, small to large
	small_likes_large_photo_id_timeline = []
	for m in feeds.find({"$and":[{"likes.data.id":small['id']},{"collected_from.id":large['id']},{"type":"photo"}]},{"id":1,"_id":0}):
		small_likes_large_photo_id_timeline.append(m)
	pair['small_likes_large_photo_id_timeline'] = small_likes_large_photo_id_timeline
	pair['small_likes_large_photo_count_timeline'] = len(small_likes_large_photo_id_timeline)

	small_comments_on_large_photo_id_timeline = []
	for m in feeds.find({"$and":[{"comments.data.from.id":small['id']},{"collected_from.id":large['id']},{"type":"photo"}]},{"id":1,"_id":0}):
		small_comments_on_large_photo_id_timeline.append(m)
	pair['small_comments_on_large_photo_id_timeline'] = small_comments_on_large_photo_id_timeline
	pair['small_comments_on_large_photo_count_timeline'] = len(small_comments_on_large_photo_id_timeline)

	small_is_tagged_in_large_photo_id_timeline = []
	for m in feeds.find({"$and":[{"with_tags.data.id":small['id']},{"collected_from.id":large['id']},{"type":"photo"}]},{"id":1,"_id":0}):
		small_is_tagged_in_large_photo_id_timeline.append(m)
	pair['small_is_tagged_in_large_photo_id_timeline'] = small_is_tagged_in_large_photo_id_timeline
	pair['small_is_tagged_in_large_photo_count_timeline'] = len(small_is_tagged_in_large_photo_id_timeline)
	
	# photo, large to small
	large_likes_small_photo_id_timeline = []
	for m in feeds.find({"$and":[{"likes.data.id":large['id']},{"collected_from.id":small['id']},{"type":"photo"}]},{"id":1,"_id":0}):
		large_likes_small_photo_id_timeline.append(m)
	pair['large_likes_small_photo_id_timeline'] = large_likes_small_photo_id_timeline
	pair['large_likes_small_photo_count_timeline'] = len(large_likes_small_photo_id_timeline)

	large_comments_on_small_photo_id_timeline = []
	for m in feeds.find({"$and":[{"comments.data.from.id":large['id']},{"collected_from.id":small['id']},{"type":"photo"}]},{"id":1,"_id":0}):
		large_comments_on_small_photo_id_timeline.append(m)
	pair['large_comments_on_small_photo_id_timeline'] = large_comments_on_small_photo_id_timeline
	pair['large_comments_on_small_photo_count_timeline'] = len(large_comments_on_small_photo_id_timeline)

	large_is_tagged_in_small_photo_id_timeline = []
	for m in feeds.find({"$and":[{"with_tags.data.id":large['id']},{"collected_from.id":small['id']},{"type":"photo"}]},{"id":1,"_id":0}):
		large_is_tagged_in_small_photo_id_timeline.append(m)
	pair['large_is_tagged_in_small_photo_id_timeline'] = large_is_tagged_in_small_photo_id_timeline
	pair['large_is_tagged_in_small_photo_count_timeline'] = len(large_is_tagged_in_small_photo_id_timeline)
	
	# status, small to large
	small_likes_large_status_id_timeline = []
	for m in feeds.find({"$and":[{"likes.data.id":small['id']},{"collected_from.id":large['id']},{"type":{"$in":["status","note"]}}]},{"id":1,"_id":0}):
		small_likes_large_status_id_timeline.append(m)
	pair['small_likes_large_status_id_timeline'] = small_likes_large_status_id_timeline
	pair['small_likes_large_status_count_timeline'] = len(small_likes_large_status_id_timeline)

	small_comments_on_large_status_id_timeline = []
	for m in feeds.find({"$and":[{"comments.data.from.id":small['id']},{"collected_from.id":large['id']},{"type":{"$in":["status","note"]}}]},{"id":1,"_id":0}):
		small_comments_on_large_status_id_timeline.append(m)
	pair['small_comments_on_large_status_id_timeline'] = small_comments_on_large_status_id_timeline
	pair['small_comments_on_large_status_count_timeline'] = len(small_comments_on_large_status_id_timeline)

	small_is_tagged_in_large_status_id_timeline = []
	for m in feeds.find({"$and":[{"with_tags.data.id":small['id']},{"collected_from.id":large['id']},{"type":{"$in":["status","note"]}}]},{"id":1,"_id":0}):
		small_is_tagged_in_large_status_id_timeline.append(m)
	pair['small_is_tagged_in_large_status_id_timeline'] = small_is_tagged_in_large_status_id_timeline
	pair['small_is_tagged_in_large_status_count_timeline'] = len(small_is_tagged_in_large_status_id_timeline)
	
	# status, large to small
	large_likes_small_status_id_timeline = []
	for m in feeds.find({"$and":[{"likes.data.id":large['id']},{"collected_from.id":small['id']},{"type":{"$in":["status","note"]}}]},{"id":1,"_id":0}):
		large_likes_small_status_id_timeline.append(m)
	pair['large_likes_small_status_id_timeline'] = large_likes_small_status_id_timeline
	pair['large_likes_small_status_count_timeline'] = len(large_likes_small_status_id_timeline)

	large_comments_on_small_status_id_timeline = []
	for m in feeds.find({"$and":[{"comments.data.from.id":large['id']},{"collected_from.id":small['id']},{"type":{"$in":["status","note"]}}]},{"id":1,"_id":0}):
		large_comments_on_small_status_id_timeline.append(m)
	pair['large_comments_on_small_status_id_timeline'] = large_comments_on_small_status_id_timeline
	pair['large_comments_on_small_status_count_timeline'] = len(large_comments_on_small_status_id_timeline)

	large_is_tagged_in_small_status_id_timeline = []
	for m in feeds.find({"$and":[{"with_tags.data.id":large['id']},{"collected_from.id":small['id']},{"type":{"$in":["status","note"]}}]},{"id":1,"_id":0}):
		large_is_tagged_in_small_status_id_timeline.append(m)
	pair['large_is_tagged_in_small_status_id_timeline'] = large_is_tagged_in_small_status_id_timeline
	pair['large_is_tagged_in_small_status_count_timeline'] = len(large_is_tagged_in_small_status_id_timeline)

	# post, small to large
	small_likes_large_post_id_timeline = []
	for m in feeds.find({"$and":[{"likes.data.id":small['id']},{"collected_from.id":large['id']},{"type":{"$in":["link","video"]}}]},{"id":1,"_id":0}):
		small_likes_large_post_id_timeline.append(m)
	pair['small_likes_large_post_id_timeline'] = small_likes_large_post_id_timeline
	pair['small_likes_large_post_count_timeline'] = len(small_likes_large_post_id_timeline)

	small_comments_on_large_post_id_timeline = []
	for m in feeds.find({"$and":[{"comments.data.from.id":small['id']},{"collected_from.id":large['id']},{"type":{"$in":["link","video"]}}]},{"id":1,"_id":0}):
		small_comments_on_large_post_id_timeline.append(m)
	pair['small_comments_on_large_post_id_timeline'] = small_comments_on_large_post_id_timeline
	pair['small_comments_on_large_post_count_timeline'] = len(small_comments_on_large_post_id_timeline)

	small_is_tagged_in_large_post_id_timeline = []
	for m in feeds.find({"$and":[{"with_tags.data.id":small['id']},{"collected_from.id":large['id']},{"type":{"$in":["link","video"]}}]},{"id":1,"_id":0}):
		small_is_tagged_in_large_post_id_timeline.append(m)
	pair['small_is_tagged_in_large_post_id_timeline'] = small_is_tagged_in_large_post_id_timeline
	pair['small_is_tagged_in_large_post_count_timeline'] = len(small_is_tagged_in_large_post_id_timeline)
	
	# post, large to small
	large_likes_small_post_id_timeline = []
	for m in feeds.find({"$and":[{"likes.data.id":large['id']},{"collected_from.id":small['id']},{"type":{"$in":["link","video"]}}]},{"id":1,"_id":0}):
		large_likes_small_post_id_timeline.append(m)
	pair['large_likes_small_post_id_timeline'] = large_likes_small_post_id_timeline
	pair['large_likes_small_post_count_timeline'] = len(large_likes_small_post_id_timeline)

	large_comments_on_small_post_id_timeline = []
	for m in feeds.find({"$and":[{"comments.data.from.id":large['id']},{"collected_from.id":small['id']},{"type":{"$in":["link","video"]}}]},{"id":1,"_id":0}):
		large_comments_on_small_post_id_timeline.append(m)
	pair['large_comments_on_small_post_id_timeline'] = large_comments_on_small_post_id_timeline
	pair['large_comments_on_small_post_count_timeline'] = len(large_comments_on_small_post_id_timeline)

	large_is_tagged_in_small_post_id_timeline = []
	for m in feeds.find({"$and":[{"with_tags.data.id":large['id']},{"collected_from.id":small['id']},{"type":{"$in":["link","video"]}}]},{"id":1,"_id":0}):
		large_is_tagged_in_small_post_id_timeline.append(m)
	pair['large_is_tagged_in_small_post_id_timeline'] = large_is_tagged_in_small_post_id_timeline
	pair['large_is_tagged_in_small_post_count_timeline'] = len(large_is_tagged_in_small_post_id_timeline)

	# item ownership: who made the post action
	# "from"
	# photo, small to large
	small_likes_large_photo_id_action = []
	for m in feeds.find({"$and":[{"likes.data.id":small['id']},{"from.id":large['id']},{"type":"photo"}]},{"id":1,"_id":0}):
		small_likes_large_photo_id_action.append(m)
	pair['small_likes_large_photo_id_action'] = small_likes_large_photo_id_action
	pair['small_likes_large_photo_count_action'] = len(small_likes_large_photo_id_action)

	small_comments_on_large_photo_id_action = []
	for m in feeds.find({"$and":[{"comments.data.from.id":small['id']},{"from.id":large['id']},{"type":"photo"}]},{"id":1,"_id":0}):
		small_comments_on_large_photo_id_action.append(m)
	pair['small_comments_on_large_photo_id_action'] = small_comments_on_large_photo_id_action
	pair['small_comments_on_large_photo_count_action'] = len(small_comments_on_large_photo_id_action)

	small_is_tagged_in_large_photo_id_action = []
	for m in feeds.find({"$and":[{"with_tags.data.id":small['id']},{"from.id":large['id']},{"type":"photo"}]},{"id":1,"_id":0}):
		small_is_tagged_in_large_photo_id_action.append(m)
	pair['small_is_tagged_in_large_photo_id_action'] = small_is_tagged_in_large_photo_id_action
	pair['small_is_tagged_in_large_photo_count_action'] = len(small_is_tagged_in_large_photo_id_action)

	# photo, large to small
	large_likes_small_photo_id_action = []
	for m in feeds.find({"$and":[{"likes.data.id":large['id']},{"from.id":small['id']},{"type":"photo"}]},{"id":1,"_id":0}):
		large_likes_small_photo_id_action.append(m)
	pair['large_likes_small_photo_id_action'] = large_likes_small_photo_id_action
	pair['large_likes_small_photo_count_action'] = len(large_likes_small_photo_id_action)

	large_comments_on_small_photo_id_action = []
	for m in feeds.find({"$and":[{"comments.data.from.id":large['id']},{"from.id":small['id']},{"type":"photo"}]},{"id":1,"_id":0}):
		large_comments_on_small_photo_id_action.append(m)
	pair['large_comments_on_small_photo_id_action'] = large_comments_on_small_photo_id_action
	pair['large_comments_on_small_photo_count_action'] = len(large_comments_on_small_photo_id_action)

	large_is_tagged_in_small_photo_id_action = []
	for m in feeds.find({"$and":[{"with_tags.data.id":large['id']},{"from.id":small['id']},{"type":"photo"}]},{"id":1,"_id":0}):
		large_is_tagged_in_small_photo_id_action.append(m)
	pair['large_is_tagged_in_small_photo_id_action'] = large_is_tagged_in_small_photo_id_action
	pair['large_is_tagged_in_small_photo_count_action'] = len(large_is_tagged_in_small_photo_id_action)
	
	# status, small to large
	small_likes_large_status_id_action = []
	for m in feeds.find({"$and":[{"likes.data.id":small['id']},{"from.id":large['id']},{"type":{"$in":["status","note"]}}]},{"id":1,"_id":0}):
		small_likes_large_status_id_action.append(m)
	pair['small_likes_large_status_id_action'] = small_likes_large_status_id_action
	pair['small_likes_large_status_count_action'] = len(small_likes_large_status_id_action)

	small_comments_on_large_status_id_action = []
	for m in feeds.find({"$and":[{"comments.data.from.id":small['id']},{"from.id":large['id']},{"type":{"$in":["status","note"]}}]},{"id":1,"_id":0}):
		small_comments_on_large_status_id_action.append(m)
	pair['small_comments_on_large_status_id_action'] = small_comments_on_large_status_id_action
	pair['small_comments_on_large_status_count_action'] = len(small_comments_on_large_status_id_action)

	small_is_tagged_in_large_status_id_action = []
	for m in feeds.find({"$and":[{"with_tags.data.id":small['id']},{"from.id":large['id']},{"type":{"$in":["status","note"]}}]},{"id":1,"_id":0}):
		small_is_tagged_in_large_status_id_action.append(m)
	pair['small_is_tagged_in_large_status_id_action'] = small_is_tagged_in_large_status_id_action
	pair['small_is_tagged_in_large_status_count_action'] = len(small_is_tagged_in_large_status_id_action)

	# status, large to small
	large_likes_small_status_id_action = []
	for m in feeds.find({"$and":[{"likes.data.id":large['id']},{"from.id":small['id']},{"type":{"$in":["status","note"]}}]},{"id":1,"_id":0}):
		large_likes_small_status_id_action.append(m)
	pair['large_likes_small_status_id_action'] = large_likes_small_status_id_action
	pair['large_likes_small_status_count_action'] = len(large_likes_small_status_id_action)

	large_comments_on_small_status_id_action = []
	for m in feeds.find({"$and":[{"comments.data.from.id":large['id']},{"from.id":small['id']},{"type":{"$in":["status","note"]}}]},{"id":1,"_id":0}):
		large_comments_on_small_status_id_action.append(m)
	pair['large_comments_on_small_status_id_action'] = large_comments_on_small_status_id_action
	pair['large_comments_on_small_status_count_action'] = len(large_comments_on_small_status_id_action)

	large_is_tagged_in_small_status_id_action = []
	for m in feeds.find({"$and":[{"with_tags.data.id":large['id']},{"from.id":small['id']},{"type":{"$in":["status","note"]}}]},{"id":1,"_id":0}):
		large_is_tagged_in_small_status_id_action.append(m)
	pair['large_is_tagged_in_small_status_id_action'] = large_is_tagged_in_small_status_id_action
	pair['large_is_tagged_in_small_status_count_action'] = len(large_is_tagged_in_small_status_id_action)

	# post, small to large
	small_likes_large_post_id_action = []
	for m in feeds.find({"$and":[{"likes.data.id":small['id']},{"from.id":large['id']},{"type":{"$in":["link","video"]}}]},{"id":1,"_id":0}):
		small_likes_large_post_id_action.append(m)
	pair['small_likes_large_post_id_action'] = small_likes_large_post_id_action
	pair['small_likes_large_post_count_action'] = len(small_likes_large_post_id_action)

	small_comments_on_large_post_id_action = []
	for m in feeds.find({"$and":[{"comments.data.from.id":small['id']},{"from.id":large['id']},{"type":{"$in":["link","video"]}}]},{"id":1,"_id":0}):
		small_comments_on_large_post_id_action.append(m)
	pair['small_comments_on_large_post_id_action'] = small_comments_on_large_post_id_action
	pair['small_comments_on_large_post_count_action'] = len(small_comments_on_large_post_id_action)

	small_is_tagged_in_large_post_id_action = []
	for m in feeds.find({"$and":[{"with_tags.data.id":small['id']},{"from.id":large['id']},{"type":{"$in":["link","video"]}}]},{"id":1,"_id":0}):
		small_is_tagged_in_large_post_id_action.append(m)
	pair['small_is_tagged_in_large_post_id_action'] = small_is_tagged_in_large_post_id_action
	pair['small_is_tagged_in_large_post_count_action'] = len(small_is_tagged_in_large_post_id_action)
	
	# post, large to small
	large_likes_small_post_id_action = []
	for m in feeds.find({"$and":[{"likes.data.id":large['id']},{"from.id":small['id']},{"type":{"$in":["link","video"]}}]},{"id":1,"_id":0}):
		large_likes_small_post_id_action.append(m)
	pair['large_likes_small_post_id_action'] = large_likes_small_post_id_action
	pair['large_likes_small_post_count_action'] = len(large_likes_small_post_id_action)

	large_comments_on_small_post_id_action = []
	for m in feeds.find({"$and":[{"comments.data.from.id":large['id']},{"from.id":small['id']},{"type":{"$in":["link","video"]}}]},{"id":1,"_id":0}):
		large_comments_on_small_post_id_action.append(m)
	pair['large_comments_on_small_post_id_action'] = large_comments_on_small_post_id_action
	pair['large_comments_on_small_post_count_action'] = len(large_comments_on_small_post_id_action)

	large_is_tagged_in_small_post_id_action = []
	for m in feeds.find({"$and":[{"with_tags.data.id":large['id']},{"from.id":small['id']},{"type":{"$in":["link","video"]}}]},{"id":1,"_id":0}):
		large_is_tagged_in_small_post_id_action.append(m)
	pair['large_is_tagged_in_small_post_id_action'] = large_is_tagged_in_small_post_id_action
	pair['large_is_tagged_in_small_post_count_action'] = len(large_is_tagged_in_small_post_id_action)
	
	# post to timeline, small to large
	small_posts_photo_video_to_large_timeline_id = []
	for m in feeds.find({"$and":[{"from.id":small['id']},{"collected_from.id":large['id']},{"type":{"$in":["photo","video"]}}]},{"id":1,"_id":0}):
		small_posts_photo_video_to_large_timeline_id.append(m)
	pair['small_posts_photo_video_to_large_timeline_id'] = small_posts_photo_video_to_large_timeline_id
	pair['small_posts_photo_video_to_large_timeline_count'] = len(small_posts_photo_video_to_large_timeline_id)

	small_posts_post_to_large_timeline_id = []
	for m in feeds.find({"$and":[{"from.id":small['id']},{"collected_from.id":large['id']},{"type":{"$in":["link","note"]}}]},{"id":1,"_id":0}):
		small_posts_post_to_large_timeline_id.append(m)
	for m in feeds.find({"$and":[{"story_tags.data.id":small['id']},{"collected_from.id":large['id']},{"status_type":"wall_post"}]},{"id":1,"_id":0}):
		if m not in small_posts_post_to_large_timeline_id:
			small_posts_post_to_large_timeline_id.append(m)
	pair['small_posts_post_to_large_timeline_id'] = small_posts_post_to_large_timeline_id
	pair['small_posts_post_to_large_timeline_count'] = len(small_posts_post_to_large_timeline_id)

	# post to timeline, large to small
	large_posts_photo_video_to_small_timeline_id = []
	for m in feeds.find({"$and":[{"from.id":large['id']},{"collected_from.id":small['id']},{"type":{"$in":["photo","video"]}}]},{"id":1,"_id":0}):
		large_posts_photo_video_to_small_timeline_id.append(m)
	pair['large_posts_photo_video_to_small_timeline_id'] = large_posts_photo_video_to_small_timeline_id
	pair['large_posts_photo_video_to_small_timeline_count'] = len(large_posts_photo_video_to_small_timeline_id)

	large_posts_post_to_small_timeline_id = []
	for m in feeds.find({"$and":[{"from.id":large['id']},{"collected_from.id":small['id']},{"type":{"$in":["link","note"]}}]},{"id":1,"_id":0}):
		large_posts_post_to_small_timeline_id.append(m)
	for m in feeds.find({"$and":[{"story_tags.data.id":small['id']},{"collected_from.id":large['id']},{"status_type":"wall_post"}]},{"id":1,"_id":0}):
		if m not in large_posts_post_to_small_timeline_id:
			large_posts_post_to_small_timeline_id.append(m)
	pair['large_posts_post_to_small_timeline_id'] = large_posts_post_to_small_timeline_id
	pair['large_posts_post_to_small_timeline_count'] = len(large_posts_post_to_small_timeline_id)

	return pair
