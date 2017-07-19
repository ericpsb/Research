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
request.post(options, function(err, res, body) {
    let json = JSON.parse(body);
    accessToken = json.token;
    console.log(json);
});

// get all likes from server side
app.post('/likes', function(req, res) {
    console.log('express app called successful');
    likesPrediction(req, function(result) {
        res.json({
             result: result 
        });
    });
});

app.post('/posts', function(req, res) {
    console.log('express app called successful');
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
        callback(JSON.parse(body).predictions); 
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
        console.log(err);
        if ((JSON.parse(body)).status == 403) {
            console.log('error in posts prediction');
        }
        console.log(JSON.parse(body));
        callback(JSON.parse(body).predictions);
    });
}
 

var privateKey = fs.readFileSync('privkey.pem', 'utf8');
var certificate = fs.readFileSync('cert.pem', 'utf8');
var credentials = {key: privateKey, cert: certificate};
var httpsServer = https.createServer(credentials, app);

httpsServer.listen(8000, '0.0.0.0');
