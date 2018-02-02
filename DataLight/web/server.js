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

httpsServer.listen(8001, '0.0.0.0');

app.use(bodyParser.json());
app.use(express.static(__dirname));

var msPredictions = [];
var msPredictions_scaled = [];
var likeResults = [];
var postResults = [];
var allPosts = [];
var allLikes = [];
var likeInfo = [];
var likeResult_raw = [];
var contributor_names = [];
var postInfo = [];
/*
var contributor_posts = [];
var post1_result = [];
var post2_result = [];
var post3_result = [];
var post4_result = [];
var post5_result = [];
var temp = [];
*/

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
    //searchPostsCallback();
    //console.log(mailQuiz);
    const mailOptions = {
        from: 'datalightdaslab@gmail.com',
        to: email,
        subject: 'Survey',
        html:   
              '<h3>How you present yourself</h3>' +
              '<p>Agreeableness: ' + Math.round(msPredictions_scaled[0].value) + '%</p>' +  
              '<p>The most influential Facebook likes are '     
                    + contributor_names[0].value[0] + ', ' 
                    + contributor_names[0].value[1] + ', '
                    + contributor_names[0].value[2] + '</p>' + 
              '<p>Here is a post where you express ' + Math.round(msPredictions_scaled[0].value) + '% agreeableness</p>' +
              '<p>' + postInfo[0] + '</p>' +
              '</br>' + 
              '<p>Conscientiousness: ' + Math.round(msPredictions_scaled[1].value) + '%</p>' +  
              '<p>The most influential Facebook likes are '    
                    + contributor_names[1].value[0] + ', ' 
                    + contributor_names[1].value[1] + ', '
                    + contributor_names[1].value[2] + '</p>' +
              '<p>Here is a post where you express ' + Math.round(msPredictions_scaled[1].value) + '% conscientiousness</p>' +
              '<p>' + postInfo[1] + '</p>' +
              '</br>' + 
              '<p>Neoroticism: ' + Math.round(msPredictions_scaled[2].value) + '%</p>' +  
              '<p>The most influential Facebook likes are '    
                    + contributor_names[2].value[0] + ', ' 
                    + contributor_names[2].value[1] + ', '
                    + contributor_names[2].value[2] + '</p>' + 
              '<p>Here is a post where you express ' + Math.round(msPredictions_scaled[2].value) + '% neoroticism</p>' +
              '<p>' + postInfo[2] + '</p>' +
              '</br>' + 
              '<p>Extraversion : ' + Math.round(msPredictions_scaled[3].value) + '%</p>' +  
              '<p>The most influential Facebook likes are '    
                    + contributor_names[3].value[0] + ', ' 
                    + contributor_names[3].value[1] + ', '
                    + contributor_names[3].value[2] + '</p>' +  
              '<p>Here is a post where you express ' + Math.round(msPredictions_scaled[3].value) + '% extraversion</p>' +
              '<p>' + postInfo[3] + '</p>' +
              '</br>' + 
              '<p>Openness: ' + Math.round(msPredictions_scaled[4].value) + '%</p>' +  
              '<p>The most influential Facebook likes are '    
                    + contributor_names[4].value[0] + ', ' 
                    + contributor_names[4].value[1] + ', '
                    + contributor_names[4].value[2] + '</p>' +
              '<p>Here is a post where you express ' + Math.round(msPredictions_scaled[4].value) + '% openness</p>' +
              '<p>' + postInfo[4] + '</p>' +
              '</br>' + 
              '<h3>How you see yourself</h3>' +
              '<p>Agreeableness: ' + mailQuiz[0] + '%</p>' +  
              '<p>Conscientiousness: ' + mailQuiz[1] + '%</p>' +  
              '<p>Neoroticism: ' + mailQuiz[2] + '%</p>' +  
              '<p>Extraversion : ' + mailQuiz[3] + '%</p>' +  
              '<p>Openness: ' + mailQuiz[4] + '%</p>'+
              '<br />' +
              '<p>Please complete the survey below, it should take less than 10 minutes</p>' +
              '<a href="#">Survey</a>'


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
        'customer_id' : 3518,
        'api_key' : 'qni7cb0q4cvi3l9cgpcpfv1ikb'
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
    

function findContributors() {
    var predictions = [];
    predictions = [ 
        { trait: 'BIG5_Agreeableness', value: likeResults_raw.predictions[0].value },
        { trait: 'BIG5_Conscientiousness', value: likeResults_raw.predictions[3].value  },
        { trait: 'BIG5_Neoroticism', value: likeResults_raw.predictions[1].value },
        { trait: 'BIG5_Extraversion', value: likeResults_raw.predictions[4].value },
        { trait: 'BIG5_Openness', value: likeResults_raw.predictions[2].value }
    ]; 
    
    var contributors = [];
    contributors = [ 
        { trait: 'BIG5_Agreeableness', positive: likeResults_raw.contributors[3].positive, negative: likeResults_raw.contributors[3].negative},
        { trait: 'BIG5_Conscientiousness', positive: likeResults_raw.contributors[2].positive, negative: likeResults_raw.contributors[2].negative},
        { trait: 'BIG5_Neoroticism', positive: likeResults_raw.contributors[0].positive, negative: likeResults_raw.contributors[0].negative},
        { trait: 'BIG5_Extraversion', positive: likeResults_raw.contributors[4].positive, negative: likeResults_raw.contributors[4].negative},
        { trait: 'BIG5_Openness', positive: likeResults_raw.contributors[1].positive, negative: likeResults_raw.contributors[1].negative}
    ]; 
    //console.log('print predictions');
    //console.log(predictions);
    //console.log('print contributions');
    //console.log(contributors);
    
    var contributors_result = [];
    // choose which one to display based on its influence on the predictions
    for (i = 0; i < 5; i++) {
        if (predictions[i].value > 0.5) {
            contributors_result[i] = { trait: contributors[i].trait, value: contributors[i].positive };
        } else {
            contributors_result[i] = { trait: contributors[i].trait, value: contributors[i].negative };
        }
    }
    //console.log('print contributor_result');
    //console.log(contributors_result);
    searchLikes(contributors_result);
}

// extract names that influence like predictions
function searchLikes(arr) {
    //console.log('in searchLikes');
    //console.log(likeInfo);
    var value = [];
    for (k = 0; k < 5; k++ ) {
        for (i = 0; i < 3; i++) {
            for (j = 0; j < likeInfo.likeInfo.length; j++) {
                if (arr[k].value[i] === likeInfo.likeInfo[j].id) {
                    value.push(likeInfo.likeInfo[j].name);  
                    break;
                }
            }
        }
        contributor_names[k] = { trait: arr[k].trait, value: value }
        value = [];
    }
    //console.log('print contributor_names');
    //console.log(contributor_names);
}

function searchPosts(arr) {
    temp = arr.slice();
    console.log('just printing temp');
    console.log(temp);
    
    // pick 5 random posts
    /*
    for (i = temp.length-1; i > 1; i--) {
        var r = Math.floor(Math.random() * i);
        var t = temp[i];
        temp[i] = temp[r];
        temp[r] = t;
    }
    
    temp = temp.slice(0, 5); 
    */
    for (i = temp.length-1; i >= 0; i--) {
        if (temp[i].split(" ").length >= 200) {
            console.log('YES');
            postInfo[i] = temp[i];
            console.log(postInfo[i]);
        } else {
            console.log('NO');
            postInfo[i] = "We don't have enough data to show post that most influences the predictions";
            console.log(postInfo[i]);
        }
    }

/*
    postPrediction(temp[1], function(result) {
        post2_result = result;
        console.log('log result');
        console.log(post2_result);
    });
    postPrediction(temp[2], function(result) {
        post3_result = result;
        console.log('log result');
        console.log(post3_result);
    });
    console.log('print temp array');
    postPrediction(temp[3], function(result) {
        post4_result = result;
        console.log('log result');
        console.log(post4_result);
    });
    postPrediction(temp[4], function(result) {
        post5_result = result;
        console.log('log result');
        console.log(post5_result);
    });
*/
}


/*
function searchPostsCallback() {
    var value1;
    var value2;
    var value3;
    var value4;
    var value5;
    console.log('print jaaaa');
    contributor_posts =  [
        { trait: 'BIG5_Agreeableness', value: post1_result[0].value, message: temp[0] },
        { trait: 'BIG5_Conscientiousness', value: post1_result[1].value, message: temp[0] },
        { trait: 'BIG5_Neoroticism', value: post1_result[2].value, message: temp[0] },
        { trait: 'BIG5_Extraversion', value: post1_result[3].value, message: temp[0] },
        { trait: 'BIG5_Openness', value: post1_result.value[4], message: temp[0] }
    ];
    if (post1_result === undefined) {
        console.log('noooo 1');
        value1 = [];
    } else {
        value1 =  post1_result[0].value;
    }
    if (post2_result === undefined) {
        console.log('noooo 2');
        value2 = [];
    } else {
        value2 =  post1_result[1].value;
    }
    if (post3_result === undefined) {
        console.log('noooo 3');
        value3 = [];
    } else {
        value3 =  post1_result[2].value;
    }
    if (post4_result === undefined) {
        console.log('noooo 4');
        value4 = [];
    } else {
        value4 =  post4_result[3].value;
    }
    if (post5_result === undefined) {
        console.log('noooo 5');
        value5 = [];
    } else {
        value5 =  post5_result[4].value;
    }
    contributor_posts =  [
        { trait: 'BIG5_Agreeableness', value: value1 },
        { trait: 'BIG5_Conscientiousness', value: value2 },
        { trait: 'BIG5_Neoroticism', value: value3 },
        { trait: 'BIG5_Extraversion', value: value4 },
        { trait: 'BIG5_Openness', value: value5}
    ];
    console.log('YASSS');
    console.log(contributor_posts);
}
*/

function calculateMSPredictions(callback1, callback2) {
    msPredictions = [ 
        { trait: 'BIG5_Agreeableness', value: (likeResults[0].value + postResults[0].value)/2 },
        { trait: 'BIG5_Conscientiousness', value: (likeResults[1].value + postResults[2].value)/2 },
        { trait: 'BIG5_Neoroticism', value: (likeResults[2].value + postResults[4].value)/2 },
        { trait: 'BIG5_Extraversion', value: (likeResults[3].value + postResults[3].value)/2 },
        { trait: 'BIG5_Openness', value: (likeResults[4].value + postResults[1].value)/2 }
    ]; 
    callback1();
    callback2(email);
    //console.log('inside calculateMSPredictions');
    //console.log(msPredictions);
    //console.log('inside calculateMSPredictions');
    //console.log(msPredictions_scaled);
}


// convert raw quiz score using TIPI reverse score method 
// and call toPercentile to convert the quizz scores to percentile
var mailQuiz = [];
function toTIPI(arr, callback) {
    for (i = 0; i < 5; i++) {
        mailQuiz[i] = (Number(arr.quizzes[i]) + Number((100 - arr.quizzes[i+5])))/2.0;
    }
    //console.log('toTIPI');
    console.log(mailQuiz);
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
    //console.log('quizzResults in toPercentile');
    //console.log(quizzesResults);
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
        { trait: 'BIG5_Agreeableness', value: distributions[0].ppf(msPredictions[0].value) },
        { trait: 'BIG5_Conscientiousness', value: distributions[1].ppf(msPredictions[1].value) },
        { trait: 'BIG5_Neoroticism', value: distributions[2].ppf(msPredictions[2].value) },
        { trait: 'BIG5_Extraversion', value: distributions[3].ppf(msPredictions[3].value) },
        { trait: 'BIG5_Openness', value: distributions[4].ppf(msPredictions[4].value) }
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
        qs: {
            'traits': 'BIG5',
            'contributors': 'true'
        },
        body: JSON.stringify(req.body.allLikes) 
    }
    request.post(options, function(err, res, body) {
        // handle accessToken expiration
        /*
        if ((JSON.parse(body)).status == 403) {
            console.log('error 403 in likes prediction');
            getAccessToken(function() {
                likesPrediction(req, callback);
            });
        } else {
        */
            callback(JSON.parse(body).predictions); 
            likeResults_raw = JSON.parse(body);
            //console.log('print likeResults_raw');
            //console.log(likeResults_raw);
            findContributors();
        //}
    });       
}

// call Magic Sauce post API
function postsPrediction(req, callback) {
    //console.log('print allPosts');
    //console.log(req.body.allPosts);
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
        } else if ((JSON.parse(body)).status == 429) {
            console.log('error 429, exceed API limit');
        } else {
            //console.log('print status code');
            console.log(JSON.parse(body).status);
            callback(JSON.parse(body).predictions);
            console.log('print out status code');
            console.log((JSON.parse(body)).status);
            //console.log('print result');
            //console.log(JSON.parse(body).predictions);
            console.log('print allPosts');
            console.log(req.body.allPosts);
            allPosts = req.body.allPosts;
            searchPosts(allPosts);
        }
    });
}

// call Magic Sauce post API for *1* post only
function postPrediction(req, callback) {
    //console.log('print allPosts');
    //console.log(req.body.allPosts);
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
        body: req
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
var email;    
// get user's email, call sendMail to send email 
app.post('/mail', function(req, res) {
    res.json({
        result: "success"
    });
    //console.log('inside mail endpoint');
    //console.log(req.body.email);
    email = req.body.email
    calculateMSPredictions(toPercent, sendMail);
    //sendMail(req.body.email);
    
});

// get all likes from client  side
app.post('/likes', function(req, res) {
    //console.log('printing out allLikes');
    allLikes = req.body;
    //console.log(allLikes);
    likesPrediction(req, function(result) {
        likeResults = result;
        //console.log('printing like predicitons from likes endpoint');
        //console.log(likeResults);
        res.json({
             result: likeResults 
        });
    });
});

app.post('/likeinfo', function(req, res) {
    //console.log('printing out likeinfo');
    likeInfo = req.body;
    //console.log(likeInfo);
    res.json({
        result: "success"
    });
});

// get all posts from client side 
app.post('/posts', function(req, res) {
    postsPrediction(req, function(result) {
        postResults = result;
        console.log('print postResults from app.post');
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
    console.log('print inside post quizz from client');
    console.log(req.body);
    toTIPI(req.body, toPercentile);
    //console.log('this is inside post quizzes endpoint');
    //console.log(req.body);
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
    //console.log('MS Predictions');
    //console.log(msPredictions);
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
