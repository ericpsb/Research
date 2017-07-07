var fs = require('fs');
const express = require('express');
const app = express();
const https = require('https');
const request = require('request');
app.use(express.static(__dirname));

app.get('/yay', function (req, res) {
    res.send('Hello World');
});

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

// make post request to Magic Sauce with `customer_id` and `api_key`
request.post(options, function(err, res, body) {
    let json = JSON.parse(body);
    console.log(json);
    likesPrediction(json);
    //console.log(body);
    //console.log(body.token);
});

function likesPrediction(response) {
    const options = {
        url: 'https://api.applymagicsauce.com/like_ids',
        headers: {
            'X-Auth-Token': response.token,
            'Content-type': 'application/json',
            'Accept': 'application/json'
        },
        qs: {'traits': ['trait1', 'trait2']},
        body: JSON.stringify(["22616629151", "19614945368", "355918454446304", "1152140431499664", "1798777590188959", "1109835245701916", "255232486973", "10387879804", "1517852608428848", "1338486086189725", "1649684008642414", "1021549901268100", "201924983236988", "6452638289", "21751825648", "1723334751329022", "136089586577758", "1834214823522684", "155275957894241", "1516491321936268", "132967616768538", "595155763929949", "849314875174595", "70534759244", "193486187343324", "185837218150459", "305115773870", "174179219354091", "30968512668", "1721313428084052", "686281128127086", "599091746860613", "496710990536538", "107810395970444", "246863552054855", "121288987898365", "609007899175923", "334191996715482", "284639525600", "352751268256569", "1593842870906555", "1679616822293043", "1437521676555227", "385346934830489", "156796752044", "228803477461289", "113811942295353", "668134036652131", "146910928678409", "157123397777485", "20531316728", "1614251518827491", "18468761129", "258970614435684", "148968472126606", "141179435910975", "1110363722321191", "403805216490826", "549556541752411", "1418073925159582", "514030908708895", "322940647865674", "1528115097406569", "5281959998", "359573887479380", "389005957880767", "371793389694429", "177855378952272", "309754825787494", "425309067633088", "6391689884", "435679103246483", "321117397909063", "162206187146794", "947679651971419", "21898300328", "926494824043342", "61738233764", "1318800798260799", "931335060267776", "396786737025433", "331464644422", "443196842397028", "104076956295773", "303371839754315", "26019341873", "583340581734574", "503088529742721", "174050659315503", "436075479927868", "142108719264759", "338523256282451", "120713927946143", "1420716621527331", "335287186650286", "199504240099510", "507150246035338", "1537512523160704", "240466992664258", "1627074400846593"]) 
    }
    request.post(options, function(err, res, body) {
        console.log(JSON.parse(body)); 
    });       
}


var privateKey = fs.readFileSync('privkey.pem', 'utf8');
var certificate = fs.readFileSync('cert.pem', 'utf8');
var credentials = {key: privateKey, cert: certificate};
var httpsServer = https.createServer(credentials, app);

httpsServer.listen(8000, '0.0.0.0');
console.log('this is working...');
