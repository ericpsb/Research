var fs = require('fs');
var $ = require('cheerio');

var numtopics;
var numdocs;
var pagesize;
var maxpage;
var homepageHtml;
var getDocumentsHtml;
var sorted_topic_docid;
var doc_table;
var sorted_topic_table;
var correlation_graph;
var time_series_graph;

// Note: these functions should be in sync with nodeLDA.js
function getDocumentsHtml(topic, start, end) {
	var result = $("<div></div>");
	for(var i=start; i<end; i++) {
		var docid = sorted_topic_docid[topic][i];
		var doc = doc_table[docid];
		var score = sorted_topic_table[topic][i];
		if(typeof doc === 'undefined') {continue;}
		result.append(document_template(i+1, doc.link, doc.date, score, doc.content));
	}
	return result.html();
}

function document_template(rank, link, date, score, content) {
	var score100 = (score*100).toFixed(1);
	var r = score < 0.5 ? 255 : Math.round(255-255*(score-0.5)*2);
	var g = score > 0.5 ? 255 : Math.round(255-255*(0.5-score)*2);
	return $("<div></div>").addClass("document").html((rank > 0 ? '#' + rank : '') + 
	' <span style="background: linear-gradient(45deg, rgba(' + r + ', ' + g + ', 0, 0.7) ' + Math.round(score100*0.95+4) + '%, #fff 1%, #fff ' + Math.round((100-score100)*0.95) + '%);">' +
	'[<span title="' + score + '">' + score100 + '%</span> ' + date + ']</span> <a href="' + link + '">' + link + '</a><br> ' +  content);
}
// End note

function loadData() {
	var nodeLDA = JSON.parse(fs.readFileSync("nodeLDA.json", 'utf8'));
	numtopics = nodeLDA.numtopics;
	numdocs = nodeLDA.numdocs;
	pagesize = nodeLDA.pagesize;
	maxpage = nodeLDA.maxpage;
	homepageHtml = nodeLDA.homepageHtml;
	sorted_topic_docid = nodeLDA.sorted_topic_docid;
	doc_table = nodeLDA.doc_table;
	sorted_topic_table = nodeLDA.sorted_topic_table;
	correlation_graph = nodeLDA.correlation_graph;
	time_series_graph = nodeLDA.time_series_graph;
}
loadData();

var express = require('express');
var https = require('https');
var app = express();
var baseurl = ""; // e.g. "/nodeLDA"
app.use(express.static(__dirname));

app.get(baseurl + '/', function(req, res) {
	
	var tid = req.query.tid;
	var page = req.query.page;
	
	if(typeof tid === 'undefined' && typeof page === 'undefined') {
		res.set('Content-Type', 'text/html');
		res.write(homepageHtml);
		res.end();
	} else {
		tid = typeof tid === 'undefined' ? 0 : tid;
		page = typeof page === 'undefined' ? 1 : page;
		if(tid < 0) {tid = 0;}
		if(tid >= numtopics) {tid = numtopics-1;}
		page = page < 1 ? 1 : page;
		page = page > maxpage ? maxpage: page;
		var start = (page - 1) * pagesize;
		var end = page * pagesize;
		end = end > numdocs ? numdocs : end;
		res.set('Content-Type', 'text/json');
		var result = {page: page, html: getDocumentsHtml(tid, start, end)}
		res.write(JSON.stringify(result));
		res.end();
	}
});

app.get(baseurl + '/cgraph', function(req, res) {
	res.set('Content-Type', 'text/json');
	res.write(correlation_graph);
	res.end();
});

app.get(baseurl + '/tgraph', function(req, res) {
	res.set('Content-Type', 'text/json');
	var tid = req.query.tid;
	var month = req.query.month;
	if(typeof tid === 'undefined' || typeof month === 'undefined') {
		res.write(time_series_graph);
		res.end();
		return;
	} else {
		var result = [];
		var topic_array = sorted_topic_table[tid];
		var doc_array = sorted_topic_docid[tid];
		for(var i=0; i<topic_array.length; i++) {
			var doc = doc_table[doc_array[i]];
			if(doc.datenum == month) {
				var d = new Date(Date.parse(doc.date)).getDate();
				result.push({x: d, y: topic_array[i], html: $("<div></div>").append(document_template(-1, doc.link, doc.date, topic_array[i], doc.content)).html()});
			}
		}
		res.write(JSON.stringify(result));
		res.end();
	}
});

var privateKey  = fs.readFileSync('privkey.pem', 'utf8');
var certificate = fs.readFileSync('cert.pem', 'utf8');
var credentials = {key: privateKey, cert: certificate};
var httpsServer = https.createServer(credentials, app);

httpsServer.listen(8080, '0.0.0.0');

//app.listen(8080, '0.0.0.0');

console.log("Server running");