import pymongo
import json
i = ""
try:
     i = json.loads(sys.argv[1])
except :
     print "ERROR"
     sys.exit(1)
client = MongoClient('localhost', 27017)
db2 = client['fbapp-DB']
collection2 = db2['fb-users']
collection3 = db2['fb-interactions']
user = collection2.find_one({"user id":str(i)})
if "json" in user:
   js = json.dumps(True)
   print js
else:
   js = json.dumps(False)
   print js
     
   
