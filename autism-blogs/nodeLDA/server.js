const fs = require('fs');
const $ = require('cheerio');

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
var topic_table_diag;
var topic_prob;
var topics;

// Note: these functions should be in sync with nodeLDA.js
function getDocumentsHtml(topic, start, end) {
	var result = $("<div></div>");
	for(var i=start; i<end; i++) {
		var docid = sorted_topic_docid[topic][i];
		var doc = doc_table[docid];
		var score = sorted_topic_table[topic][i];
		result.append(document_template("#" + (i+1) + " ", doc.link, doc.date, score, doc.content, true));
	}
	return result.html();
}

function document_template(prefix, link, date, score, content, color) {
	var span = score + ' ' + date;
	if (color == true) {
		var score100 = (score*100).toFixed(1);
		var r = score < 0.5 ? 255 : Math.round(255-255*(score-0.5)*2);
		var g = score > 0.5 ? 255 : Math.round(255-255*(0.5-score)*2);
		// we don't want color to be unseenable when the value is too low, so we set a lower bound of 4 percent
		span = '<span style="border: 1px solid #ccc; background: linear-gradient(45deg, rgba(' + r + ', ' + g + ', 0, 0.7) ' + Math.round(score100*0.95+4) + '%, #fff 1%, #fff ' +
		Math.round((100-score100)*0.95) + '%);">' + '<span title="' + score + '">' + score100 + '%</span> ' + date + '</span>';
	}
	return $("<div></div>").addClass("document").html(prefix + span + ' <a href="' + link + '" target="_blank">' + link + '</a><br> ' +  content);
}
// End note

function getCorrDocumentsHtml(t1, t2, docids) {
	var result = [];
	for(var i=0; i<docids.length; i++) {
		var id = docids[i];
		var doc = doc_table[id];
		var valt1 = topic_table_diag[t1][id];
		var valt2 = topic_table_diag[t2][id];
		var prefix = '<span class="t1">' + (valt1*100).toFixed(1) + '%</span> vs. <span class="t2">' + (valt2*100).toFixed(1) + '%</span><br>'
		result.push(document_template(prefix, doc.link, doc.date, "", doc.content, false));
	}
	return result.reduce(function(sum, val) {return sum + val;}, "");
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
	correlation_graph = nodeLDA.correlation_graph;
	time_series_graph = nodeLDA.time_series_graph;
	topic_table_diag = nodeLDA.topic_table_diag;
	topic_prob = nodeLDA.topic_prob;
	topics = nodeLDA.topics;
}
loadData();

const express = require('express');
const https = require('https');
const app = express();
const baseurl = ""; // e.g. "/nodeLDA"
app.use(express.static(__dirname));

// homepage + pages for each topic
app.get(baseurl + '/', function(req, res) {
	var tid = req.query.tid;
	var page = req.query.page;
	// return homepage
	if(typeof tid === 'undefined' && typeof page === 'undefined') {
		res.set('Content-Type', 'text/html');
		res.send(homepageHtml);
		res.end();
	// return a computed page for just the document section
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
		res.json({page: page, html: getDocumentsHtml(tid, start, end)});
		res.end();
	}
});

app.get(baseurl + '/cgraph', function(req, res) {
	res.set('Content-Type', 'text/json');
	res.send(correlation_graph);
	res.end();
});

app.get(baseurl + '/tgraph', function(req, res) {
	res.set('Content-Type', 'text/json');
	var tid = req.query.tid;
	var month = req.query.month;
	if(typeof tid === 'undefined' || typeof month === 'undefined') {
		res.send(time_series_graph);
		res.end();
		return;
	} else { // ts zoom graph data
		if(tid < 0 || tid >= sorted_topic_table.length) {
			res.sendStatus(400).end();
			return;
		}
		var result = [];
		var topic_array = sorted_topic_table[tid];
		var doc_array = sorted_topic_docid[tid];
		for(var i=0; i<topic_array.length; i++) {
			var doc = doc_table[doc_array[i]];
			if(doc.datenum == month) {
				var d = new Date(Date.parse(doc.date)).getDate();
				result.push({x: d, y: topic_array[i], html: $("<div></div>").append(document_template("", doc.link, doc.date, "", doc.content, false)).html()});
			}
		}
		result.sort(function(a, b) {return a.x == b.x ? a.y - b.y : a.x - b.x;});
		
		res.json(result);
		res.end();
	}
});

app.get(baseurl + '/corr', function(req, res) {
	res.set('Content-Type', 'text/json');
	var t1 = req.query.t1;
	var t2 = req.query.t2;
	var div1 = $("<div></div>");
	var div2 = $("<div></div>");
	var div3 = $("<div></div>");
	var graph = $('<svg width="200" height="200" preserveAspectRatio="none"></svg>');
	const cutoff = 0.05;
	var data = [];
	
	var endx = 0;
	var endy = 0;
	for(var i=0; i<numdocs; i++) {
		if(topic_table_diag[t1][i] < cutoff || topic_table_diag[t2][i] < cutoff) {continue;}
		var y = topic_table_diag[t1][i] - cutoff;
		var x = topic_table_diag[t2][i] - cutoff;
		var r = Math.sqrt(x*x + y*y);
		if(r < 0.02) {continue;} // omitting docs just around the cutoff origin since they all get mapped to the center column
		var ang =  Math.asin(y/r);
		ang += Math.PI/4;
		y = r*Math.sin(ang)*100;
		x = Math.round(r*Math.cos(ang)*60)*2; // Math.round(r*Math.cos(ang)*maxColumnsOnEachSide)*SpacingBetweenColumn; 
		data.push({doc: i, x: x, y: y});
		endx = Math.abs(x)+1 > endx ? Math.abs(x)+1 : endx;
	}
	data.sort(function(a, b) {return b.x == a.x ? b.y - a.y : a.x - b.x;});
	var lastX = 0;
	var array = [];
	var cumlen = [];
	var docids = [];
	var dump = function() {
		var y = array.length;
		if(y == 0) {return;}
		for(var i=0; i<array.length; i++) {
			docids.push(array[i].doc);
		}
		var x = array[0].x;
		endy = y/1.5 > endy ? y/1.5 : endy;
		var color = "#bf5240";
		if (x < 0) {
			var dx = -x/endx;
			color = "rgb(" + Math.round(191+(255-191)*dx) + ", " + Math.round(82-(165-82)*dx) + ", " + Math.round(64-(64-0)*dx) + ")";
		} else if(x > 0) {
			var dx = x/endx;
			color = "rgb(" + Math.round(191-(191-128)*dx) + ", " + Math.round(82-(82-0)*dx) + ", " + Math.round(64+(128-64)*dx) + ")";
		}
		if(y == 1) {
			graph.append($("<ellipse></ellipse>").attr("cx", x).attr("cy", 0).attr("rx", 0.5).attr("data-index", cumlen.length).css("fill", color));
		} else {
			graph.append($("<rect></rect>").attr("x", x-0.5).attr("y", -y/2).attr("width", 1).attr("height", y).attr("data-index", cumlen.length).css("fill", color));
		}
		cumlen.push(array.length + (cumlen.length == 0 ? 0 : cumlen[cumlen.length-1]));
	}
	for(var i=0; i<data.length; i++) {
		var e = data[i];
		if(e.x != lastX) {
			dump();
			lastX = e.x;
			array = [];
		}
		array.push(e);
	}
	dump();
	
	endy = endy < 20 ? 20 : endy;
	graph.children("ellipse").attr("ry", endy/endx/2);
	
	var total = topic_prob[t1] + topic_prob[t2];
	var w1 = topic_prob[t1]/total*100;
	w1 = w1 < 20 ? 20 : w1;
	w1 = w1 > 80 ? 80 : w1;
	var w2 = 100 - w1;
	
	graph.attr("viewBox", (-endx) + " " + (-endy) + " " + (endx*2) + " " + (endy*2));
	div1.append($("<div></div>").append($("<span></span>").append(topics[t1] + "<br>" + topic_prob[t1] + " documents").addClass("t1"))).addClass("left").css("width", "calc(" + w1.toFixed(1) + "% + 98px)");
	div2.append(graph).addClass("mid").css("left", "calc(" + w1.toFixed(1) + "% - 102px)");
	div3.append($("<div></div>").append($("<span></span>").append(topics[t2]  + "<br>" + topic_prob[t2] + " documents").addClass("t2")).css("float", "right")).addClass("right").css("width", "calc(" + w2.toFixed(1) + "% + 98px)").css("float", "right");
	res.json({cumlen: cumlen, docids: docids, graph: $("<div></div>").append(div1).append(div2).append(div3).html()});
	res.end();
});

app.get(baseurl + '/corrdocs', function(req, res) {
	var t1 = req.query.t1;
	var t2 = req.query.t2;
	var docids = req.query.docids;
	res.send(getCorrDocumentsHtml(t1, t2, docids));
	res.end();
});

// comment out this block and uncomment app.listen if you are using http instead of https
const privateKey  = fs.readFileSync('privkey.pem', 'utf8');
const certificate = fs.readFileSync('cert.pem', 'utf8');
const credentials = {key: privateKey, cert: certificate};
const httpsServer = https.createServer(credentials, app);
httpsServer.listen(8080, '0.0.0.0');

//app.listen(8080, '0.0.0.0');

console.log("Server running");