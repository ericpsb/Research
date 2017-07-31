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
        self.name = ""
        self.mongo = mongo_access.MongoAccess()
        self.nodes = []
        self.links = []
        self.pairs = []
        self.people = []

    def generate_viz(self):
        """Generate JSON and insert into database."""
        user = self.mongo.get_user_from_db(self.uid)
        if user is None:
            # TODO[P]: throw error
            return

        self.name = user['name']
        self.nodes.append({'name': self.name})
        self.people.append({
            'name' : self.name,
            'id' : self.uid,
            'collected_from' : [
                {
                    'name' : self.name,
                    'id' : self.uid
                }
            ]
        })

        json = self.generate_viz_json()
        user['json'] = json
        self.mongo.update_user_db(self.uid, user)
        self.mongo.insert_many_interactions(self.pairs)
        self.mongo.insert_many_people(self.people)

    def generate_viz_json(self):
        """Generate JSON."""
        # Feed documents
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
            self.explode_document(document)

        # Event documents
        event_query = {
            'attended_by.0.id' : self.uid,
            'rsvp_status' : 'attending'
        }
        events = self.mongo.query_events(event_query)
        for document in events:
            self.explode_event(document)

        self.generate_links()

        return {
            'nodes': self.nodes,
            'links': self.links
        }

    def generate_links(self):
        """Generate links between all nodes and assign values."""

        ########################################################################
        # TODO[P]: Still need to add functionality for book/music links and    #
        # a check for when someone posts to your timeline, because that's an   #
        # automatic 5 for the value.                                           #
        ########################################################################

        link_values = {
            'like': 2,
            'comment': 3,
            'tag': 4,
            'co-like': 1,
            'co-comment': 2,
            'co-tag': 5
        }

        for pair in self.pairs:
            source_node = self.nodes.index({'name': pair['source']})
            target_node = self.nodes.index({'name': pair['target']})
            value = 0

            for interaction in pair['data']:
                if interaction[0] == 'photo':
                    value += link_values[interaction[1]]
                elif interaction[0] == 'event':
                    value += 2
                else:
                    value += link_values[interaction[2]]

            self.links.append({'source': source_node, 'target': target_node, 'value': value})

        return

    def explode_document(self, document):
        """Take individual feed document and turn into many pair interactions."""

        ########################################################################
        # TODO[P]: Try to only grab person once per feed item. So maybe have a #
        # hierarchy of what's important... though have all interactions count  #
        # towards visualization weights.                                       #
        # NOTE: story_tags also tag the person who posted it (I think), so we  #
        #       may have to account for that.                                  #
        # NOTE: Also need to do something about page likes...                  #
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
                    if ((option[0] == 'story_tags' and 'type' in document
                            and (document['type'] == 'wall_post' or document['type'] == 'photo'))
                            or (option[0] == 'with_tags' or option[0] == 'comments' or option[0] == 'likes')):
                        interactions = self.process_status(document, option[1])
                        self.generate_pairs(self.name, option[2], option[4], interactions)

        else:
            for option in options:
                if self.is_in_list(option):
                    if ((option[0] == 'story_tags' and 'type' in document
                            and (document['type'] == 'wall_post' or document['type'] == 'photo'))
                            or (option[0] == 'with_tags' or option[0] == 'comments' or option[0] == 'likes')):
                        interactions = self.process_status(document, option[1])
                        self.add_to_people_collection(document['from'])
                        self.generate_single_pair(self.name, option[3], document['from']['name'], interactions)
                        interactions = self.process_status(document, 'co-' + option[1])
                        self.generate_pairs(self.name, option[3], option[4], interactions)
        
        # Generate pairs for every other person related to each other
        for option in options:
            if option[4] is not None:
                if ((option[0] == 'story_tags' and 'type' in document
                     and (document['type'] == 'wall_post' or document['type'] == 'photo'))
                        or option[0] != 'story_tags'):
                    # The fact that I'm copying this line again is probably not great, but not a
                    # huge priority for me right now.
                    interactions = self.process_status(document, 'co-' + option[1])
                    for user in option[4]:
                        if 'type' in user and user['type'] != 'user':
                            continue
                        if 'from' in user:
                            self.generate_pairs(user['from']['name'], option[2], option[4], interactions)
                        else:
                            self.generate_pairs(user['name'], option[2], option[4], interactions)

        return

    def explode_event(self, document):
        """Take individual event document and turn into many pair interactions."""
        interactions = self.process_event(document)
        self.generate_pairs(self.name, 'source', document['attending']['data'], interactions)
        return

    def generate_pairs(self, username, direction, other_users, interactions):
        """Generates all pairs for given list of users and appends to object list."""
        if direction == 'source':
            for user in other_users:
                self.add_to_people_collection(user)
                if 'from' in user:
                    if user['from']['name'] == username or user['from']['id'] == self.uid:
                        continue
                    pair = self.get_user_pair(username, user['from']['name'])
                    if {'name': user['from']['name']} not in self.nodes:
                        self.nodes.append({'name': user['from']['name']})
                else:
                    if user['name'] == username or user['id'] == self.uid:
                        continue
                    if 'type' in user and user['type'] == 'page':
                        continue
                    pair = self.get_user_pair(username, user['name'])
                    if {'name': user['name']} not in self.nodes:
                        self.nodes.append({'name': user['name']})

                pair['data'].append(interactions)
                self.pairs.append(pair)
        else:
            for user in other_users:
                self.add_to_people_collection(user)
                if 'from' in user:
                    if user['from']['name'] == username or user['from']['id'] == self.uid:
                        continue
                    pair = self.get_user_pair(user['from']['name'], username)
                    if {'name': user['from']['name']} not in self.nodes:
                        self.nodes.append({'name': user['from']['name']})
                else:
                    if user['name'] == username or user['id'] == self.uid:
                        continue
                    if 'type' in user and user['type'] == 'page':
                        continue
                    pair = self.get_user_pair(user['name'], username)
                    if {'name': user['name']} not in self.nodes:
                        self.nodes.append({'name': user['name']})

                pair['data'].append(interactions)
                self.pairs.append(pair)

    def generate_single_pair(self, username, direction, other_user, interactions):
        """Generates single pair and appends to object list."""
        if direction == 'source':
            pair = self.get_user_pair(username, other_user)
        else:
            pair = self.get_user_pair(other_user, username)
        pair['data'].append(interactions)
        if {'name': other_user} not in self.nodes:
            self.nodes.append({'name': other_user})
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

    def find_person_in_list(self, name):
        """Find person in existing list."""
        for index, person in enumerate(self.people):
            if person['name'] == name:
                return self.people.pop(index)
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

    def process_event(self, document):
        """Create an interaction array for an event."""
        interaction_type = "event"
        name = document['name']
        description = document['description'] if 'description' in document else ""
        cover = document['cover']['source'] if 'cover' in document else ""
        start_date = datetime.datetime.strptime(document['start_time'][:-5],
                                                  '%Y-%m-%dT%H:%M:%S').strftime('%m/%d/%y')

        return [interaction_type, name, description, cover, start_date]

    def add_to_people_collection(self, user):
        """Add person to people list."""
        person_id = user['from']['id'] if 'from' in user else user['id']
        person_name = user['from']['name'] if 'from' in user else user['name']
        person = self.find_person_in_list(person_name)
        
        if person is None:
            person = {
                'name' : person_name,
                'id' : person_id,
                'collected_from' : [
                    {
                        'name' : self.name,
                        'id' : self.uid
                    }
                ]
            }
        else:
            if {'id' : self.uid, 'name' : self.name} not in person['collected_from']:
                person['collected_from'].append({
                    'id' : self.uid,
                    'name' : self.name
                })
        
        self.people.append(person)
