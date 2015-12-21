var mongodb = require('mongodb');

//We need to work with "MongoClient" interface in order to connect to a mongodb server.
var MongoClient = mongodb.MongoClient;

// Connection URL. This is where your mongodb server is running.
var url = 'mongodb://localhost:27017/fbapp-DB';
var A = "";
var B= "";
var myCollection;
var doc;

function getInteractions(a,b){
	var interactions=[];
    A = a;
    B = b;
    // Use connect method to connect to the Server
    var db = MongoClient.connect(url, function(err, db) {
    if(err)
        throw err;
    myCollection = db.collection('fb-interactions');
    doc = myCollection.findOne({'source':A,'target':B});
  });

  return doc['data'];

}
