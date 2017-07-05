var fs = require('fs');
const express = require('express')
const app = express()
const https = require('https');
app.use(express.static(__dirname));

app.get('/', function (req, res) {
    res.send('Hello World')
})

var privateKey = fs.readFileSync('privkey.pem', 'utf8');
var certificate = fs.readFileSync('cert.pem', 'utf8');
var credentials = {key: privateKey, cert: certificate};
var httpsServer = https.createServer(credentials, app);

httpsServer.listen(8000, '0.0.0.0');
console.log('this is working...');
