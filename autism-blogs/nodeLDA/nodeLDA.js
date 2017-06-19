// Get all the necessary module
var pp = require('preprocess');
var fs = require('fs');
var $ = require('cheerio');

console.log("reading files");
// Loads the files from the local directory
var topicfile = fs.readFileSync('topic_frame.csv', 'utf8');
var docfile = fs.readFileSync('documents.txt', 'utf8');
var html = fs.readFileSync('jslda.html', 'utf8');

console.log("processing topics");
// preprocess topics
var topiclines = topicfile.split("\n");
var topics = topiclines[0].split(",");
topics.splice(0, 1);
topics.forEach(function(e, i, a){a[i] = e.replace(/_/g, ', ');});
var numtopics = topics.length;

// preprocess topic value
topiclines.splice(0, 1); // delete topic lineHeight
topiclines.splice(topiclines.length-1, 1); // delete empty line added by write.csv
var numdocs = topiclines.length;
console.log(numdocs + " documents found");
var topic_table = []; // 2d table of the topic values

topiclines.forEach(function(element, index, array) {
	var vals = element.split(",");
	vals.push(vals.splice(0, 1)); // throw the doc_id(first value) to last place
	topic_table.push(vals);
});

// process topic values

var sorted_topic_table = new Array(numtopics);
var sorted_topic_docid = new Array(numtopics);
var topic_sort_map = new Array(numtopics);
for(var i=0; i<numtopics; i++) {
	sorted_topic_table[i] = new Array(numdocs);
	sorted_topic_docid[i] = new Array(numdocs);
	topic_sort_map[i] = {avg: 0, index: i, back: -1};
}

for(var i=0; i<numtopics; i++) {
	topic_table.sort(function(a, b) {return b[i] - a[i];}); // sort the table on a specific topic
	for(var j=0; j<numdocs; j++) {
		var val = parseFloat(topic_table[j][i]);
		topic_sort_map[i].avg += val;
		sorted_topic_table[i][j] = val;
		sorted_topic_docid[i][j] = topic_table[j][numtopics]-1; // docid start with 1
	}
}

// the index of the map will the topic order that got displayed on the page
// while the index attribute in the object is the topic order in the data structure
topic_sort_map.forEach(function(e){
	e.avg /= numdocs;
});
topic_sort_map.sort(function(a, b) {return b.avg - a.avg;})

for(var i=0; i < topic_sort_map.length; i++) {
	topic_sort_map[topic_sort_map[i].index].back = i;
}

function sort_array_with_map(array) {
	var temp = array.slice(0);
	for(var i=0; i < topic_sort_map.length; i++) {
		array[i] = temp[topic_sort_map[i].index]; 
	}
}

// sort the other arrays acccording to the map
sort_array_with_map(sorted_topic_table);
sort_array_with_map(sorted_topic_docid);
sort_array_with_map(topics);

// process topics
function topic_template(topic, avg){ return $('<div></div>').attr("title", "average: " + avg).addClass('topicwords').html(topic); };

var topic_dom = $("<div></div>");
topics.forEach(function(e, i ,a) {topic_dom.append(topic_template(e, topic_sort_map[i].avg));})
topic_dom.children('div').first().addClass("selected");

// topic correlation

var corrlation_table = new Array(numtopics);
var topic_prob = new Array(numtopics);
for(var i=0; i<numtopics; i++) {
	var temp = new Array(numtopics);
	for(var j=0; j< numtopics; j++) {
		temp[j] = 0;
	}
	corrlation_table[i] = temp;
	topic_prob[i] = 0;
}

topic_table.forEach(function(doc) {
	var doc_topic = new Array();
	for(var topic = 0; topic < numtopics; topic++) {
		if(parseFloat(doc[topic]) > 0.05) {
			doc_topic.push(topic_sort_map[topic].back);
			topic_prob[topic_sort_map[topic].back]++; // Count the number of docs with this topic
		}
	}
	// Look at all pairs of topics that occur in the document.
	for(var i=0; i < doc_topic.length - 1; i++) {
		for(var j=i+1; j < doc_topic.length; j++) {
			corrlation_table[ doc_topic[i] ][ doc_topic[j] ]++;
			corrlation_table[ doc_topic[j] ][ doc_topic[i] ]++;
		}
	}
});

for(var t1=0; t1 < numtopics-1; t1++) {
	for(var t2=t1+1; t2 < numtopics; t2++) {
		var denom = topic_prob[t1] * topic_prob[t2];
		corrlation_table[t1][t2] = Math.log((numdocs * corrlation_table[t1][t2]) / denom);
		corrlation_table[t2][t1] = Math.log((numdocs * corrlation_table[t2][t1]) / denom);
	}
}

function getShortTopic(topic) {
	return topic.split(", ", 3).join(", ");
}

function getCorrelationGraphHtml() {
	console.log("generating correlation graph");
	var xmin = 50;
	var xmax = 950;
	var ymin = 150;
	var ymax = 1050;
	var textPadding = 150;
	var graph = $("<svg></svg>").attr("width", "78%").attr("height", ymax*2).attr("viewBox", "0 0 " + (xmax+textPadding) + " " + (ymax + 2*textPadding)).attr("preserveAspectRatio", "xMinYMin meet");
	var topicScale = (ymax-ymin) / numtopics;
	var circleScale = function(val) {return Math.sqrt(val / ((ymax-ymin)/(2*numtopics))) * (topicScale/2);};
	
	for(var i=0; i<numtopics; i++) {
		var hor = $("<text></text>").addClass("hor").attr("x", xmax).attr("y", ymin + i*topicScale).html(getShortTopic(topics[i]));
		var ver = $("<text></text>").addClass("ver").attr("x", xmin + i*topicScale).attr("y", ymax).attr("transform", "rotate(45, " + (xmin + i*topicScale) + ", " + ymax + ")").html(getShortTopic(topics[i]));
		var vertop = $("<text></text>").addClass("ver").attr("x", xmin + i*topicScale).attr("y", (ymin-10)).attr("transform", "rotate(-45, " + (xmin + i*topicScale) + ", " + (ymin-10) + ")").html(getShortTopic(topics[i]));
		graph.append(hor);
		graph.append(ver);
		graph.append(vertop);
	}
	
	for(var t1=0; t1 < numtopics-1; t1++) {
		for(var t2=t1+1; t2 < numtopics; t2++) {
			var val = corrlation_table[t1][t2];
			var circle = $("<circle></circle>").attr("cx", xmin + t1*topicScale).attr("cy", ymin + t2*topicScale).attr("r", circleScale(Math.abs(val))).attr("title", topics[t1] + ' /<br>' + topics[t2]).css("fill", val > 0 ? "#88f" : "#f88");
			var circle2 = $("<circle></circle>").attr("cx", xmin + t2*topicScale).attr("cy", ymin + t1*topicScale).attr("r", circleScale(Math.abs(val))).attr("title", topics[t2] + ' /<br>' + topics[t1]).css("fill", val > 0 ? "#88f" : "#f88");
			graph.append(circle);
			graph.append(circle2);
		}
	}

	return $("<div></div>").append(graph).html();
}

console.log("processing documents")
// preprocess documents
var documents = docfile.split("\n");
documents.splice(documents.length-1, 1); // remove empty line added by script
if(numdocs !== documents.length) {console.log("Warning: document count mismatch: " + numdocs + ' vs. ' + documents.length);}
var doc_table = [];

var firstM = 99999;
var lastM = 0;

documents.forEach(function(element, index, array) {
	var e = element.split("\t");
	if(isNaN(Date.parse(e[1]))) { // no date given from csv
		// try to find date in url
		var l = e[0];
		var m = l.match("20[0-9][0-9]/(?:0?[0-9]|1[0-2])/(?:0?[0-9]|[1-2][0-9]|3[0-1]])");
		if( m != null ) {
			var d = new Date(Date.parse(m[0]));
			var dn = d.getFullYear()*12+d.getMonth();
			doc_table[index] = {link: e[0], date: d.toLocaleDateString(), content: e[2], datenum: dn};
			firstM = dn < firstM ? dn : firstM;
			lastM = dn > lastM ? dn : lastM;
			return;
		}
		m = l.match("20[0-9][0-9]/(?:0?[0-9]|1[0-2])");
		if( m != null ) {
			var d = new Date(Date.parse(m[0]));
			var mon = d.getMonth() + 1;
			var dn = d.getFullYear()*12+d.getMonth();
			doc_table[index] = {link: e[0], date: d.getFullYear() + "-" + (mon < 10 ? "0" + mon : mon) + "-??", content: e[2], datenum: dn};
			firstM = dn < firstM ? dn : firstM;
			lastM = dn > lastM ? dn : lastM;
			return;
		}
		m = l.match("20[0-9][0-9]");
		if( m != null ) {
			var d = new Date(Date.parse(m[0]));
			doc_table[index] = {link: e[0], date: d.getFullYear() + "-??-??", content: e[2], datenum: -1};
			return;
		}
		doc_table[index] = {link: e[0], date: "????-??-??", content: e[2], datenum: -1};
	} else {
		var d = new Date(Date.parse(e[1]));
		var dn = d.getFullYear()*12+d.getMonth();
		doc_table[index] = {link: e[0], date: d.toLocaleDateString(), content: e[2], datenum: dn};
		firstM = dn < firstM ? dn : firstM;
		lastM = dn > lastM ? dn : lastM;
	}
	
});

function document_template(rank, link, date, score, content) {
	var score100 = (score*100).toFixed(1);
	var r = score < 0.5 ? 255 : Math.round(255-255*(score-0.5)*2);
	var g = score > 0.5 ? 255 : Math.round(255-255*(0.5-score)*2);
	return $("<div></div>").addClass("document").html('#' + rank + 
	' <span style="background: linear-gradient(45deg, rgba(' + r + ', ' + g + ', 0, 0.7) ' + Math.round(score100*0.95+4) + '%, #fff 1%, #fff ' + Math.round((100-score100)*0.95) + '%);">' +
	'[<span title="' + score + '">' + score100 + '%</span> ' + date + ']</span> <a href="' + link + '">' + link + '</a><br> ' +  content);
}

function getDocumentsHtml(topic, start, end) {
	var result = $("<div></div>");
	for(var i=start; i<end; i++) {
		var docid = sorted_topic_docid[topic][i];
		var doc = doc_table[docid];
		var score = sorted_topic_table[topic][i];
		result.append(document_template(i+1, doc.link, doc.date, score, doc.content));
	}
	return result.html();
}

// time series graph
function getTimeSeriesGraphHtml() {
	console.log("generating time series graph");
	var h = 110;
	var w = 500;
	var months = lastM - firstM + 1;
	var w1 = w/months;
	var result = $("<div></div>");
	var toprate = 0.0015; // tweak this value if the y axis is too small (increase this) or too large (decrease this)
	for(var topic=0; topic < numtopics; topic++) {
		var data = new Array(months);
		for(var t=0; t<months; t++) {data[t] = 0;}
		var valrow = sorted_topic_table[topic];
		var docrow = sorted_topic_docid[topic];
		for(var i=0; i<valrow.length; i++) {
			var doc = doc_table[docrow[i]];
			if(doc.datenum < 0) {continue;}
			data[doc.datenum-firstM] += valrow[i];
		}
		var d = "M0,"+h;
		for(var i=0; i<data.length; i++) {
			data[i] = data[i]/numdocs;
			d+="L" + (i*w1) + "," + (h-h*data[i]/toprate);
		}
		d+="L" + ((data.length-1)*w1) + "," + h + "Z";
		var svg = $("<svg></svg>").attr("width", w).attr("height", h).attr("viewBox", "0 0 " + w + " " + h).attr("preserveAspectRatio", "xMinYMin meet");
		var g = $("<g></g>");
		var path = $("<path></path>").attr("d", d).css("fill", "#ccc");
		var text = $("<text></text>").attr("x", 5).attr("y", 20).html(topics[topic]);
		g.append(path)
		g.append(text);
		svg.append(g);
		result.append(svg);
	}
	return result.html();
}

function getTimeRange() {
	var first = firstM%12+1;
	var fin = lastM%12+1;
	return text = "The time range is from " + Math.floor(firstM/12) + "-" + (first < 10 ? "0" + first : first) + " to " + Math.floor(lastM/12) + "-" + (fin < 10 ? "0" + fin : fin) + ".";
}

const pagesize = 35;
const maxpage = Math.floor(numdocs/pagesize+1);
var homepageHtml = pp.preprocess(html, {TOPICS: topic_dom.html(), DOCS: getDocumentsHtml(0, 0, pagesize),
MAXPAGE: maxpage, CGRAPH: getCorrelationGraphHtml(), TGRAPH: getTimeSeriesGraphHtml(), MINM: firstM, MAXM: lastM});

console.log("dumping data to file");
var nodeLDA = {};
nodeLDA.numtopics = numtopics;
nodeLDA.numdocs = numdocs;
nodeLDA.pagesize = pagesize;
nodeLDA.maxpage = maxpage;
nodeLDA.homepageHtml = homepageHtml;
nodeLDA.doc_table = doc_table;
nodeLDA.sorted_topic_docid = sorted_topic_docid;
nodeLDA.sorted_topic_table = sorted_topic_table;

fs.writeFileSync("nodeLDA.json", JSON.stringify(nodeLDA), {encoding: 'utf8'});