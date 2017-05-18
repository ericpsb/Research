import ConfigParser

CONFIG = ConfigParser.SafeConfigParser()
CONFIG.read("config.ini")
USER_DB = CONFIG.get("Database", "user-db")
FB_INFO_DB = CONFIG.get("Database", "facebook-info-db")
