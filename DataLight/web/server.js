const fs = require('fs');
const express = require('express');
const app = express();
const https = require('https');
const request = require('request');
const bodyParser = require('body-parser');
const gaussian = require('gaussian');
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

// get accessToken once the server is running
getAccessToken(function() {
        console.log("get token success");
});
    

var likeResults = [];
// get all likes from client  side
app.post('/likes', function(req, res) {
    likesPrediction(req, function(result) {
        likeResults = result;
        console.log('printing like predicitons');
        console.log(likeResults);
        console.log(likeResults[0].value);
        res.json({
             result: likeResults 
        });
    });
});

var postResults = [];
// get all posts from client side 
app.post('/posts', function(req, res) {
    postsPrediction(req, function(result) {
        postResults = result;
        console.log('printing post predictions');
        console.log(postResults);
        res.json({
             result: postResults 
        });
    });
});

app.post('/quizzes', function(req, res) {
    res.json({
        result: 'success'
    });
    toTIPI(req.body, toPercentile);
});

// acting as an endpoint for light show to get Magic Sauce prediction
app.get('/mspredictions', function(req, res) {    
    // average of likes prediction and posts prediction
    const msPredictions = [ 
        { trait: 'BIG5_Agreeableness', value: (likeResults[0].value + postResults[0].value)/2 },
        { trait: 'BIG5_Conscientiousness', value: (likeResults[1].value + postResults[2].value)/2 },
        { trait: 'BIG5_Neoroticism', value: (likeResults[2].value + postResults[4].value)/2 },
        { trait: 'BIG5_Extraversion', value: (likeResults[3].value + postResults[3].value)/2 },
        { trait: 'BIG5_Openness', value: (likeResults[4].value + postResults[1].value)/2 }
    ] 
    console.log('MS Predictions');
    console.log(msPredictions);
    res.json({
        result: msPredictions
    });
});

// acting as an endpoint for light show to get quiz result 
app.get('/quizzes', function(req, res) {
    res.json({
        result: quizzesResults
    });
});
    
// convert raw quiz score using TIPI reverse score method 
function toTIPI(arr, callback) {
    var quizzResults = [];
    for (i = 0; i < 5; i++) {
        quizzResults[i] = (Number(arr.quizzes[i]) + Number((100 - arr.quizzes[i+5])))/2.0;
    }
    // convert to percentile
    callback(quizzResults);
}
 
// processed quiz result
var quizzesResults = [];
function toPercentile(arr) {
    const agreeableness = gaussian(66.4, Math.pow(18.3, 2));
    const conscientiousness = gaussian(63.8, Math.pow(18.3, 2));
    const neurotism = gaussian(51.0, Math.pow(21.9, 2));
    const openness = gaussian(74.5, Math.pow(16.4, 2));
    const extraversion = gaussian(54.6, Math.pow(22.6, 2));
    
    const distributions = [agreeableness, neurotism, openness, conscientiousness, extraversion];
    quizzesResults = [ 
        { trait: 'BIG5_Agreeableness', value: distributions[0].cdf(arr[0]) },
        { trait: 'BIG5_Conscientiousness', value: distributions[1].cdf(arr[1]) },
        { trait: 'BIG5_Neoroticism', value: distributions[2].cdf(arr[2]) },
        { trait: 'BIG5_Extraversion', value: distributions[3].cdf(arr[3]) },
        { trait: 'BIG5_Openness', value: distributions[4].cdf(arr[4]) }
    ] 
}

// call Magic Sauce like API
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
        // handle accessToken expiration
        if ((JSON.parse(body)).status == 403) {
            console.log('error 403 in likes prediction');
            getAccessToken(function() {
                likesPrediction(req, callback);
            });
        } else {
            callback(JSON.parse(body).predictions); 
        }
    });       
}

// call Magic Sauce post API
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
 
var privateKey = fs.readFileSync('privkey.pem', 'utf8');
var certificate = fs.readFileSync('cert.pem', 'utf8');
var credentials = {key: privateKey, cert: certificate};
var httpsServer = https.createServer(credentials, app);

httpsServer.listen(8000, '0.0.0.0');
