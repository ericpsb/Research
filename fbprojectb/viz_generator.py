#!/usr/bin/env python
"""Contains class for VisualizationGenerator"""

import datetime
import mongo_access

class VisualizationGenerator(object):
    """Generate visualization JSON for user.

    This class generates the visualization JSON (nodes and links) for a user,
    and additionally generates all of the interactions between the user and
    other Facebook users and inserts in the the database.abs
    """

    def __init__(self, userid):
        """Initialize class variables."""
        self.uid = userid
        self.mongo = mongo_access.MongoAccess()
        self.nodes = []
        self.links = []
        self.pairs = []

    def generate_viz(self):
        """Generate JSON and insert into database."""
        user = self.mongo.get_user_from_db(self.uid)
        if user is None:
            # TODO[P]: throw error
            return

        self.nodes.append({'name': user['name']})

        json = self.generate_viz_json(user['name'])
        user['json'] = json
        self.mongo.update_user_db(self.uid, user)

    def generate_viz_json(self, username):
        """Generate JSON."""
        node_index = 1
        link_index = 0

        feed_query = {
            '$or' : [
                {'from.id' : self.uid},
                {'comments.data' : {'$elemMatch' : {'from.id' : self.uid}}},
                {'likes.data' : {'$elemMatch' : {'id' : self.uid}}},
                {'story_tags' : {'$elemMatch' : {'id' : self.uid}}},
                {'with_tags.data' : {'$elemMatch' : {'id' : self.uid}}}
            ]
        }
        feed = self.mongo.query_feed(feed_query)

        for document in feed:
            self.explode_document(document, username)

        return ""

# ===========================================================================================
# ===========================================================================================

    def explode_document(self, document, username):
        """Take individual feed document and turn into many pair interactions."""
        # Check the following:
        # - if from id is person
        # - if in with_tags
        # - if in story_tags
        # - if in comments
        # - if in likes
        #
        # TODO[P]: Also, only grab person once per feed item. So maybe have a hierarchy of
        # what's important... though have all interactions count towards visualization
        # weights.

        # If from.id == me, then I posted it. Therefore, I have a connection with everyone
        # who commented, liked, or was tagged in this.
        # NOTE: But if I didn't post it... it doesn't mean a whole lot... it means I have a
        # connection that will be covered elsewhere.

        # All possible "status_type"s:
        # null, "added_photos", "added_video", "created_note",
        # "mobile_status_update", "published_story", "shared_story", "wall_post"

        # And all "type"s:
        # "event", "link", "music", "photo", "status", "video"

        ########################################################################
        # TODO[P] x 2!                                                         #
        #   1. Figure out how to make this all shorter and more generalized.   #
        #   2. Apply these concepts to the rest of the document types.         #
        # If that happens, this should be pretty dandy.                        #
        # NOTE: story_tags also tag the person who posted it (I think), so we  #
        #       may have to account for that.                                  #
        # NOTE: Also need to do something about events and page likes...       #
        ########################################################################
        if document['type'] == 'status':
            if document['from']['id'] == self.uid:
                if 'comments' in document:
                    interactions = self.process_status(document, 'comment')
                    self.generate_pairs(username, 'target', document['comments']['data'], interactions)
                if 'likes' in document:
                    interactions = self.process_status(document, 'like')
                    self.generate_pairs(username, 'target', document['likes']['data'], interactions)
                if 'with_tags' in document:
                    interactions = self.process_status(document, 'tag')
                    self.generate_pairs(username, 'source', document['with_tags']['data'], interactions)
                if 'story_tags' in document:
                    interactions = self.process_status(document, 'tag')
                    self.generate_pairs(username, 'source', document['story_tags'], interactions)
            else:
                if self.is_in_comments(document):
                    interactions = self.process_status(document, 'comment')
                    self.generate_single_pair(username, 'source', document['from']['name'], interactions)
                    interactions = self.process_status(document, 'co-comment')
                    self.generate_pairs(username, 'source', document['comments']['data'], interactions)
                if self.is_in_likes(document):
                    interactions = self.process_status(document, 'like')
                    self.generate_single_pair(username, 'source', document['from']['name'], interactions)
                    interactions = self.process_status(document, 'co-like')
                    self.generate_pairs(username, 'source', document['likes']['data'], interactions)
                if self.is_in_with_tags(document):
                    interactions = self.process_status(document, 'tag')
                    self.generate_single_pair(username, 'target', document['from']['name'], interactions)
                    interactions = self.process_status(document, 'co-tag')
                    self.generate_pairs(username, 'target', document['with_tags']['data'], interactions)
                if self.is_in_story_tags(document):
                    interactions = self.process_status(document, 'tag')
                    self.generate_single_pair(username, 'target', document['from']['name'], interactions)
                    interactions = self.process_status(document, 'co-tag')
                    self.generate_pairs(username, 'target', document['story_tags'], interactions)
        elif document['type'] == 'photo':
            pass
        elif document['type'] == 'link':
            pass
        elif document['type'] == 'video':
            pass
        elif document['type'] == 'event':
            pass
        elif document['type'] == 'music':
            pass
        else:
            print 'Error: unknown feed type'





        # if document['from']['id'] == self.uid:
        #     # TODO[P]: This can totally be condensed.
        #     if 'with_tags' in document:
        #         for tag in document['with_tags']['data']:
        #             print 'todo' # TODO[P]

        #     if 'story_tags' in document:
        #         for tag in document['story_tags']:
        #             if tag['id'] != self.uid:
        #                 print 'todo'

        #     if 'comments' in document:
        #         for tag in document['comments']['data']:
        #             if tag['from']['id'] != self.uid:
        #                 print 'todo'

        #     if 'likes' in document:
        #         for tag in document['likes']['data']:
        #             if tag['id'] != self.uid:
        #                 # NOTE: liker is source because they liked my thing
        #                 #       I was the target of their like
        #                 pair = self.get_user_pair(tag['name'], username)
        #                 interaction = self.process_status(document, "like")
        #                 pair['data'].append(interaction)
        #                 self.pairs.append(pair)

        # # If I'm in with_tags...


        # # etc.

        # # Co-comment
        # if 'comments' in document and self.is_in_comments(document, self.uid):
        #     pair = self.get_user_pair(username, document['from']['name'])
        #     interaction = self.process_status(document, "comment")
        #     pair['data'].append(interaction)
        #     self.pairs.append(pair)

        #     for tag in document['comments']['data']:
        #         if tag['from']['id'] != self.uid:
        #             pair = self.get_user_pair(tag['from']['name'], username)
        #             interaction = self.process_status(document, "co-comment")
        #             pair['data'].append(interaction)
        #             self.pairs.append(pair)

        # # Co-like
        # if 'likes' in document and self.is_in_likes(document, self.uid):
        #     pair = self.get_user_pair(username, document['from']['name'])
        #     interaction = self.process_status(document, "like")
        #     pair['data'].append(interaction)
        #     self.pairs.append(pair)

        #     for tag in document['likes']['data']:
        #         if tag['id'] != self.uid:
        #             pair = self.get_user_pair(tag['name'], username)
        #             interaction = self.process_status(document, "co-like")
        #             pair['data'].append(interaction)
        #             self.pairs.append(pair)

        return

# ===========================================================================================
# ===========================================================================================

    def generate_pairs(self, username, direction, other_users, interactions):
        if direction == 'source':
            for user in other_users:
                if user['id'] == self.uid:
                    continue
                pair = self.get_user_pair(username, user['name'])
                pair['data'] = interactions
                self.pairs.append(pair)
        else:
            for user in other_users:
                if user['id'] == self.uid:
                    continue
                pair = self.get_user_pair(user['name'], username)
                pair['data'] = interactions
                self.pairs.append(pair)

    def generate_single_pair(self, username, direction, other_user, interactions):
        if direction == 'source':
            pair = self.get_user_pair(username, other_user)
            pair['data'] = interactions
            self.pairs.append(pair)
        else:
            pair = self.get_user_pair(other_user, username)
            pair['data'] = interactions
            self.pairs.append(pair)
    
    def get_user_pair(self, source, target):
        """Get a user pair from existing list or create new one."""
        pair = self.find_pair_in_list(source, target)

        if pair is None:
            pair = {'source': source, 'target': target, 'data': []}
        return pair

    def find_pair_in_list(self, source, target):
        """Find user pair in existing list."""
        for index, pair in enumerate(self.pairs):
            if pair['source'] == source and pair['target'] == target:
                return self.pairs.pop(index)
        return None

    def is_in_comments(self, document):
        """Determine if a user is in comments."""
        if 'comments' not in document:
            return False

        for comment in document['comments']['data']:
            if comment['from']['id'] == self.uid:
                return True
        return False

    def is_in_likes(self, document):
        """Determine if a user is in likes."""
        if 'likes' not in document:
            return False

        for like in document['likes']['data']:
            if like['id'] == self.uid:
                return True
        return False

    def is_in_with_tags(self, document):
        """Determine if a user is in with_tags."""
        if 'with_tags' not in document:
            return False

        for tag in document['with_tags']['data']:
            if tag['id'] == self.uid:
                return True
        return False

    def is_in_story_tags(self, document):
        """Determine if a user is in story_tags."""
        if 'story_tags' not in document:
            return False

        for tag in document['story_tags']:
            if tag['id'] == self.uid:
                return True
        return False

    def process_status(self, document, given_type):
        """Create an interaction array for a user's post."""
        doc_type = document['type']
        status_type = document['status_type']
        interaction_type = given_type
        story = document['story'] if 'story' in document else ""
        message = document['message'] if 'message' in document else ""
        description = document['description'] if 'description' in document else ""
        link = document['link'] if 'link' in document else ""
        doc_id = document['id']
        video = document['video'] if 'video' in document else ""
        created_date = datetime.datetime.strptime(document['created_time'][:-5],
                                                  '%Y-%m-%dT%H:%M:%S').strftime('%m/%d/%y')

        return [doc_type, status_type, interaction_type, story, message,
                description, link, doc_id, video, created_date]

    def get_pairs(self):
        """Return pairs variable"""
        return self.pairs
