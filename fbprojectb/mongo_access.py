import config
from pymongo import MongoClient

class MongoAccess(object):

    def __init__(self):
        self.conn = MongoClient(config.get_connection_string())

    def get_users_collection(self):
        return self.conn[config.USER_DB]['fb-users']

    def get_interactions_collection(self):
        return self.conn[config.USER_DB]['fb-interactions']

    def get_feed_collection(self):
        return self.conn[config.FB_INFO_DB]['feeds']

    def get_events_collection(self):
        return self.conn[config.FB_INFO_DB]['events']

    def get_user_from_db(self, userid):
        users_collection = self.get_users_collection()
        return users_collection.find_one({'user id': userid})

    def update_user_db(self, userid, updated_user):
        users_collection = self.get_users_collection()
        users_collection.update({'user id': userid}, updated_user)

    def insert_many_interactions(self, interactions):
        interactions_collection = self.get_interactions_collection()
        interactions_collection.insert_many(interactions)

    def query_feed(self, query):
        feed_collection = self.get_feed_collection()
        return feed_collection.find(query)

    def query_events(self, query):
        events_collection = self.get_events_collection()
        return events_collection.find(query)
