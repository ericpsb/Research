const fs = require('fs');
const express = require('express');
const app = express();
const https = require('https');
const request = require('request');
const bodyParser = require('body-parser');
app.use(bodyParser.json());
app.use(express.static(__dirname));

const options = {
    url: 'https://api.applymagicsauce.com/auth', 
    headers: {
        'Content-type' : 'application/json',
        'Accept' : 'application/json'
    }, 
    body: JSON.stringify({
        'customer_id' : 3159,
        'api_key' : 'h53ego871hmljgolodj37eg8s9'
    })
    
}; 

let accessToken = '';
// make post request to Magic Sauce with `customer_id` and `api_key`
function getAccessToken(callback) {
    request.post(options, function(err, res, body) {
        let json = JSON.parse(body);
        accessToken = (JSON.parse(body)).token;
        callback();
    });
}

//getAccessToken();
    

// get all likes from client  side
app.post('/likes', function(req, res) {
    likesPrediction(req, function(result) {
        res.json({
             result: result 
        });
    });
});

// get all posts from client side 
app.post('/posts', function(req, res) {
    console.log('express app post called successful');
    postsPrediction(req, function(result) {
        res.json({
             result: result 
        });
    });
});

function likesPrediction(req, callback) {
    const options = {
        url: 'https://api.applymagicsauce.com/like_ids',
        headers: {
            'X-Auth-Token': accessToken,
            'Content-type': 'application/json',
            'Accept': 'application/json'
        },
        qs: {'traits': 'BIG5'},
        body: JSON.stringify(req.body.allLikes) 
    }
    request.post(options, function(err, res, body) {
        console.log('error 403 in likes prediction');
        // handle accessToken expiration
        if ((JSON.parse(body)).status == 403) {
            getAccessToken(function() {
                likesPrediction(req, callback);
            });
        } else {
            callback(JSON.parse(body).predictions); 
        }
    });       
}

function postsPrediction(req, callback) {
    const options = {
        url: 'https://api.applymagicsauce.com/text',
        headers: {
            'X-Auth-Token': accessToken,
            'Content-type': 'application/json',
            'Accept': 'application/json',
        },
        qs: {
            'traits': 'BIG5',
            'source': 'STATUS_UPDATE'
        },
        body: JSON.stringify(req.body.allPosts)
    }

    request.post(options, function(err, res, body) {
        // handle accessToken expiration
        if ((JSON.parse(body)).status == 403) {
            console.log('error 403 in postsPrediction');
            getAccessToken(function() {
                postsPrediction(req, callback);
            });
        } else {
            callback(JSON.parse(body).predictions);
        }
    });
}
 
app.use(function (err, req, res, next) {
    console.error(err.stack);
    res.status(403).send('acess token is expired');
});

var privateKey = fs.readFileSync('privkey.pem', 'utf8');
var certificate = fs.readFileSync('cert.pem', 'utf8');
var credentials = {key: privateKey, cert: certificate};
var httpsServer = https.createServer(credentials, app);

httpsServer.listen(8000, '0.0.0.0');
