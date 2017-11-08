const fs = require('fs');
const express = require('express');
const app = express();
const http = require('http');
const request = require('request');
const bodyParser = require('body-parser');
const gaussian = require('gaussian'); 
const nodemailer = require('nodemailer');
const exec = require('child_process').exec;
//var privateKey = fs.readFileSync('privkey.pem', 'utf8');
//var certificate = fs.readFileSync('/etc/letsencrypt/live/das-lab.org/fullchain.pem', 'utf8');
//var privateKey = fs.readFileSync('/etc/letsencrypt/live/das-lab.org/privkey.pem', 'utf8');
//var certificate = fs.readFileSync('cert.pem', 'utf8');
//var credentials = {key: privateKey, cert: certificate};
var httpsServer = http.createServer(/*credentials,*/ app);

httpsServer.listen(8000, '0.0.0.0');

app.use(bodyParser.json());
app.use(express.static(__dirname));

var msPredictions = [];
var msPredictions_scaled = [];
var likeResults = [];
var postResults = [];

console.log("server running...");
// initialize transporter object
var transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
            user: 'datalightdaslab@gmail.com',
            pass: 'daslabdatalight'
    }
});

function sendMail(email) {
    console.log(msPredictions);
    console.log(quizzesResults);
    /*
    toPercent();
    console.log('inside sendmail');
    console.log('msPredictions: ');
    console.log(msPredictions);
    console.log(msPredictions_scaled);
    */
    const mailOptions = {
        from: 'datalightdaslab@gmail.com',
        to: email,
        subject: 'DataLight Survey',
        html: '<h2>Prediction</h2>' +  
              '<h3>Magic Sauce</h3>' +
              '<p>Agreeableness: ' + msPredictions[0].value + '</p>' +  
              '<p>Conscientiousness: ' + msPredictions[1].value + '</p>' +  
              '<p>Neoroticism: ' + msPredictions[2].value + '</p>' +  
              '<p>Extraversion : ' + msPredictions[3].value + '</p>' +  
              '<p>Openness: ' + msPredictions[4].value + '</p>' +  
              '<br />' +
              '<h3>Personality Quiz</h3>' +
              '<p>Agreeableness: ' + quizzesResults[0].value + '</p>' +  
              '<p>Conscientiousness: ' + quizzesResults[1].value + '</p>' +  
              '<p>Neoroticism: ' + quizzesResults[2].value + '</p>' +  
              '<p>Extraversion : ' + quizzesResults[3].value + '</p>' +  
              '<p>Openness: ' + quizzesResults[4].value + '</p>'+
              '<br />' +
              '<p>Please complete the survey below</p>' +
              '<a href="www.dummysurvey.com">Survey</a>'


    };
    transporter.sendMail(mailOptions, function (err, info) {
        if (err) {
            console.log(err);
        } else {
            console.log(info);
        }
    });
}

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
    



function calculateMSPredictions() {
    msPredictions = [ 
        { trait: 'BIG5_Agreeableness', value: (likeResults[0].value + postResults[0].value)/2 },
        { trait: 'BIG5_Conscientiousness', value: (likeResults[1].value + postResults[2].value)/2 },
        { trait: 'BIG5_Neoroticism', value: (likeResults[2].value + postResults[4].value)/2 },
        { trait: 'BIG5_Extraversion', value: (likeResults[3].value + postResults[3].value)/2 },
        { trait: 'BIG5_Openness', value: (likeResults[4].value + postResults[1].value)/2 }
    ] 
    console.log('inside calculateMSPredictions');
    console.log(msPredictions);
}


// convert raw quiz score using TIPI reverse score method 
// and call toPercentile to convert the quizz scores to percentile
var mailQuiz = [];
function toTIPI(arr, callback) {
    for (i = 0; i < 5; i++) {
        mailQuiz[i] = (Number(arr.quizzes[i]) + Number((100 - arr.quizzes[i+5])))/2.0;
    }
    // convert to percentile
    callback(mailQuiz);
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
    console.log('quizzResults in toPercentile');
    console.log(quizzesResults);
    //console.log(distributions[0].cdf(arr[0]));
}

function toPercent() {
    const agreeableness = gaussian(66.4, Math.pow(18.3, 2));
    const conscientiousness = gaussian(63.8, Math.pow(18.3, 2));
    const neurotism = gaussian(51.0, Math.pow(21.9, 2));
    const openness = gaussian(74.5, Math.pow(16.4, 2));
    const extraversion = gaussian(54.6, Math.pow(22.6, 2));
    
    const distributions = [agreeableness, neurotism, openness, conscientiousness, extraversion];
    msPredictions_scaled = [ 
        { trait: 'BIG5_Agreeableness', value: distributions[0].ppf(msPredictions[0]) },
        { trait: 'BIG5_Conscientiousness', value: distributions[1].ppf(msPredictions[1]) },
        { trait: 'BIG5_Neoroticism', value: distributions[2].ppf(msPredictions[2]) },
        { trait: 'BIG5_Extraversion', value: distributions[3].ppf(msPredictions[3]) },
        { trait: 'BIG5_Openness', value: distributions[4].ppf(msPredictions[4]) }
    ] 
    //console.log(distributions[0].cdf(msPredictions[0]));
    //console.log(distributions[0].ppf(msPredictions[0]));
    //console.log('msPrediction inside toPercent');
    //console.log(msPredictions);
    //console.log('msPredictions_scaled inside toPercent');
    //console.log(msPredictions_scaled);
    console.log('msPredictions in toPercent');
    console.log(msPredictions);
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
    
// get user's email, call sendMail to send email 
app.post('/mail', function(req, res) {
    res.json({
        result: "success"
    });
    console.log('inside mail endpoint');
    console.log(req.body.email);
    calculateMSPredictions();
    sendMail(req.body.email);
});

// get all likes from client  side
app.post('/likes', function(req, res) {
    likesPrediction(req, function(result) {
        likeResults = result;
        console.log('printing like predicitons from likes endpoint');
        console.log(likeResults);
        res.json({
             result: likeResults 
        });
    });
});

// get all posts from client side 
app.post('/posts', function(req, res) {
    postsPrediction(req, function(result) {
        postResults = result;
        console.log('printing post predictions from posts endpoint');
        console.log(postResults);
        res.json({
             result: postResults 
        });
    });
});

// get quizz results from client side
app.post('/quizzes', function(req, res) {
    res.json({
        result: 'success'
    });
    toTIPI(req.body, toPercentile);
    console.log('this is inside post quizzes endpoint');
    console.log(req.body);
});

// acting as an endpoint for light show to get Magic Sauce prediction
app.get('/mspredictions', function(req, res) {    
    // average of likes prediction and posts prediction
    msPredictions = [ 
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
