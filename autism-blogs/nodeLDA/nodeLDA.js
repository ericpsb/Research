// Get all the necessary module
var pp = require('preprocess');
var fs = require('fs');
var $ = require('cheerio');

// Loads the files from the local directory
var topicfile = fs.readFileSync('topic_frame.csv', 'utf8');
var docfile = fs.readFileSync('documents.txt', 'utf8');
var html = fs.readFileSync('jslda.html', 'utf8');

// preprocess topics
var topiclines = topicfile.split("\n");
var topics = topiclines[0].split(",");
topics.splice(0, 1); 
var numtopics = topics.length;

function topic_template(topic){	return $('<div></div>').addClass('topicwords').html(topic); };

var topic_dom = $("<div></div>");
topics.forEach(function(e){ topic_dom.append(topic_template(e)); });
topic_dom.children('div').first().addClass("selected");

// preprocess topic value
topiclines.splice(0, 1); // delete topic lineHeight
topiclines.splice(topiclines.length-1, 1); // delete empty line added by write.csv
var numdocs = topiclines.length;
var topic_table = []; // 2d table of the topic values

topiclines.forEach(function(element, index, array) {
	var vals = element.split(",");
	vals.push(vals.splice(0, 1)); // throw the doc_id(first value) to last place
	topic_table.push(vals);
});

var sorted_topic_table = [];
var sorted_topic_docid = [];
for(var i=0; i<numtopics; i++) {
	sorted_topic_table.push([]);
	sorted_topic_docid.push([]);
}

for(var i=0; i<numtopics; i++) {
	topic_table.sort(function(a, b) {return b[i] - a[i];}); // sort the table on a specific topic
	for(var j=0; j<topic_table.length; j++) {
		sorted_topic_table[i].push(parseFloat(topic_table[j][i]));
		sorted_topic_docid[i].push(topic_table[j][numtopics]);
	}
}

// preprocess documents
var documents = docfile.split("\n");
documents.splice(documents.length-1, 1); // remove empty line added by script
if(numdocs !== documents.length) {console.log("document count mismatch: " + numdocs + ' vs. ' + documents.length);}
var doc_table = [];
documents.forEach(function(element, index, array) {
	var e = element.split("\t");
	if(isNaN(Date.parse(e[1]))) {
		console.log(index + ' ' + e[1]);
	}
	doc_table[index] = ({link: e[0], date: Date.parse(e[1]), content: e[2]});
});

function document_template(rank, link, date, score, content) {
	return $("<div></div>").addClass("document").html('#' + rank + ' <a title="' + score + '" href="' + link + '">[' + score.toFixed(3) + ' ' + new Date(date).toLocaleDateString() + ']</a> ' + content);
}

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

// free resources
topicfile = null;
docfile = null;
topiclines = null;
topic_table = null;


var express = require('express');
var app = express();
app.use(express.static(__dirname));
app.get('/', function(req, res) {
	const pagesize = 30;
	const maxpage = Math.floor(numdocs/pagesize+1);
	var tid = req.query.tid;
	var page = req.query.page;
	
	if(typeof tid === 'undefined' && typeof page === 'undefined') {
		res.set('Content-Type', 'text/html');
		res.write(pp.preprocess(html, {TOPICS: topic_dom.html(), DOCS: getDocumentsHtml(0, 0, pagesize), MAXPAGE: maxpage}));
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

var http = require('http');
http.Server(app).listen(80);
console.log("Server running");
