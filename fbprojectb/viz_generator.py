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

        ########################################################################
        # TODO[P]: Try to only grab person once per feed item. So maybe have a #
        # hierarchy of what's important... though have all interactions count  #
        # towards visualization weights.                                       #
        # NOTE: story_tags also tag the person who posted it (I think), so we  #
        #       may have to account for that.                                  #
        # NOTE: Also need to do something about events and page likes...       #
        ########################################################################

        # Format: (key in feed, given type (kind of arbitrary), direction when
        #          user is the poster, direction when not poster, data source)
        options = [
            ('comments', 'comment', 'target', 'source', document['comments']['data'] if 'comments' in document else None),
            ('likes', 'like', 'target', 'source', document['likes']['data'] if 'likes' in document else None),
            ('with_tags', 'tag', 'source', 'target', document['with_tags']['data'] if 'with_tags' in document else None),
            ('story_tags', 'tag', 'source', 'target', document['story_tags'] if 'story_tags' in document else None)
        ]
        if document['from']['id'] == self.uid:
            for option in options:
                if option[4] is not None: # if option is in document
                    interactions = self.process_status(document, option[1])
                    self.generate_pairs(username, option[2], option[4], interactions)
        else:
            for option in options:
                if self.is_in_list(option):
                    interactions = self.process_status(document, option[1])
                    self.generate_single_pair(username, option[3], document['from']['name'], interactions)
                    interactions = self.process_status(document, 'co-' + option[1])
                    self.generate_pairs(username, option[3], option[4], interactions)

        return

    def generate_pairs(self, username, direction, other_users, interactions):
        """Generates all pairs for given list of users and appends to object list."""
        if direction == 'source':
            for user in other_users:
                if user['id'] == self.uid:
                    continue
                pair = self.get_user_pair(username, user['name'])
                pair['data'].append(interactions)
                self.pairs.append(pair)
        else:
            for user in other_users:
                if user['id'] == self.uid:
                    continue
                pair = self.get_user_pair(user['name'], username)
                pair['data'].append(interactions)
                self.pairs.append(pair)

    def generate_single_pair(self, username, direction, other_user, interactions):
        """Generates single pair and appends to object list."""
        if direction == 'source':
            pair = self.get_user_pair(username, other_user)
            pair['data'].append(interactions)
            self.pairs.append(pair)
        else:
            pair = self.get_user_pair(other_user, username)
            pair['data'].append(interactions)
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

    def is_in_list(self, option_tuple):
        """Determine if a user is in a given list.

        Assumes format of "options" list in explode_document.
        """
        if option_tuple[4] is None: # given item not in document
            return False

        for item in option_tuple[4]:
            if option_tuple[0] == 'comments':
                if item['from']['id'] == self.uid:
                    return True
            else:
                if item['id'] == self.uid:
                    return True

        return False

    def process_status(self, document, given_type):
        """Create an interaction array for a user's post."""
        doc_type = document['type']
        status_type = document['status_type'] if 'status_type' in document else ""
        interaction_type = given_type
        story = document['story'] if 'story' in document else ""
        message = document['message'] if 'message' in document else ""
        description = document['description'] if 'description' in document else ""
        link = document['link'] if 'link' in document else ""
        doc_id = document['id']
        video = document['video'] if 'video' in document else ""
        created_date = datetime.datetime.strptime(document['created_time'][:-5],
                                                  '%Y-%m-%dT%H:%M:%S').strftime('%m/%d/%y')

        if doc_type == 'photo':
            return [doc_type, interaction_type, doc_id, created_date]
        else:
            return [doc_type, status_type, interaction_type, story, message,
                    description, link, doc_id, video, created_date]

    def get_pairs(self):
        """Return pairs variable"""
        return self.pairs
