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
	return $("<div></div>").addClass("document").html('#' + rank + 
	' <span style="background: linear-gradient(45deg, rgba(' + r + ', ' + g + ', 0, 0.7) ' + Math.round(score100*0.95+4) + '%, #fff 1%, #fff ' + Math.round((100-score100)*0.95) + '%);">' +
	'[<span title="' + score + '">' + score100 + '%</span> ' + date + ']</span> <a href="' + link + '">' + link + '</a><br> ' +  content);
}

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
}
loadData();

var express = require('express');
var app = express();
app.use(express.static(__dirname));

app.get('/', function(req, res) {
	
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
app.listen(8080, '0.0.0.0');

console.log("Server running");