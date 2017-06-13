import ConfigParser
import os
from urllib import quote_plus

CONFIG = ConfigParser.SafeConfigParser()
CONFIG.read("config.ini")
USER_DB = CONFIG.get("Database", "user-db")
FB_INFO_DB = CONFIG.get("Database", "facebook-info-db")

def get_connection_string():
    conn1 = CONFIG.get("Database", "db-conn-string1")
    conn2 = CONFIG.get("Database", "db-conn-string2")
    passw = quote_plus(os.environ['MONGOPASS'])
    return conn1 + passw + conn2
