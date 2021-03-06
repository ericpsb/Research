// Get all the necessary module
var pp = require('preprocess');
var fs = require('fs');
var $ = require('cheerio');

// Loads the files from the local directory
process.stdout.write("reading files...");
var topicfile = fs.readFileSync('topic_frame.csv', 'utf8');
var docfile = fs.readFileSync('documents.txt', 'utf8');
var html = fs.readFileSync('jslda.html', 'utf8');
process.stdout.write("done\n");

// preprocess topics
process.stdout.write("processing topics...\n");
var topiclines = topicfile.split("\n");
var topics = topiclines[0].split(",");
topics.splice(0, 1);
topics.forEach(function(e, i, a){a[i] = e.replace(/_/g, ', ');});
var numtopics = topics.length;

// preprocess topic value
topiclines.splice(0, 1); // delete topic lineHeight
topiclines.splice(topiclines.length-1, 1); // delete empty line added by write.csv
var numdocs = topiclines.length;
process.stdout.write("[INFO] " + numdocs + " documents x " + numtopics + " topics found\n");
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
	topic_sort_map[i] = {avg: 0, index: i, back: -1, std: 0};
}

var topic_table_diag = new Array(numtopics);
for(var i=0; i<numtopics; i++) {
	topic_table_diag[i] = new Array(numdocs);
	for(var j=0; j<numdocs; j++) {
		topic_table_diag[i][j] = parseFloat(topic_table[j][i]);
	}
}
for(var i=0; i<numtopics; i++) {
	topic_table.sort(function(a, b) {return b[i] - a[i];}); // sort the table on a specific topic
	for(var j=0; j<numdocs; j++) {
		var val = parseFloat(topic_table[j][i]);
		topic_sort_map[i].avg += val;
		sorted_topic_table[i][j] = val;
		sorted_topic_docid[i][j] = topic_table[j][numtopics]-1; // docid start with 1 in file
	}
}

// the index of the map will the topic order that got displayed on the page
// while the index attribute in the object is the topic order in the data structure
topic_sort_map.forEach(function(e){
	e.avg /= numdocs;
});
for(var i=0; i<numtopics; i++) {
	var topicavg = topic_sort_map[i].avg;
	var topicdiff = sorted_topic_table[i].map(function(el){var d = el-topicavg; return d*d;});
	topicdiff = topicdiff.reduce(function(result, val){return result + val;}, 0);
	topic_sort_map[i].std = Math.sqrt(topicdiff);
}
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
sort_array_with_map(topic_table_diag);

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
		if(parseFloat(doc[topic]) > 0.05) { // only include topic that are "relavent" to the document
			doc_topic.push(topic_sort_map[topic].back); // topic_table does not have the index sorted
			topic_prob[topic_sort_map[topic].back]++; // Count the number of docs with this topic
		}
	}
	// Look at all pairs of topics that occur in the document.
	for(var i=0; i < doc_topic.length - 1; i++) {
		for(var j=i+1; j < doc_topic.length; j++) {
			// Note: the numeric order of doc_topic[i] and doc_topic[j] cannot be determined
			corrlation_table[ doc_topic[i] ][ doc_topic[j] ]++;
			corrlation_table[ doc_topic[j] ][ doc_topic[i] ]++;
		}
	}
});

for(var t1=0; t1 < numtopics-1; t1++) {
	for(var t2=t1+1; t2 < numtopics; t2++) {
		var denom = topic_prob[t1] * topic_prob[t2];
		// Since the graph is semetric, only one half needs to be computed
		// corrlation_table[t1][t2] could produce 0, but Math.log(0) produces Infinity, however we want it to be -Inf instead
		corrlation_table[t1][t2] = corrlation_table[t1][t2] == 0 ? -1/0 : Math.log(numdocs * corrlation_table[t1][t2] / denom);
	}
}

function getShortTopic(topic) {
	return topic.split(", ", 3).join(", ");
}

function splitTopicToLines(topic, words, delimiter) {
	var result = "";
	var array = topic.split(delimiter);
	for(var i = 0; i<array.length; i+=words) {
		var last = i+words >= array.length-1;
		result += array.slice(i, (last ? array.length-1 : i+words)).join(delimiter);
		result += (last ? "" : delimiter + "<br>");
	}
	return result;
}

function getCorrelationGraphHtml() {
	process.stdout.write("generating correlation graph...");
	var xmin = 30;
	var xmax = 930;
	var ymin = 150;
	var ymax = ymin + (xmax-xmin);
	var textPadding = 170;
	var graph = $("<svg></svg>").attr("width", xmax+textPadding).attr("height", ymax + 2*textPadding).attr("viewBox", "0 0 " + (xmax+textPadding) + " " + (ymax + 2*textPadding)).attr("preserveAspectRatio", "xMinYMin meet");
	var topicScale = (ymax-ymin) / numtopics;
	var circleScale = function(val) {return isFinite(val) ? Math.sqrt(val / ((ymax-ymin)/(2*numtopics))) * (topicScale/2) : (topicScale/2);}; // if val is infinite, produce largest circle
	
	for(var i=0; i<numtopics; i++) {
		var hor = $("<text></text>").addClass("t2").attr("x", xmax).attr("y", ymin + i*topicScale).html(getShortTopic(topics[i]));
		var ver = $("<text></text>").addClass("t1").attr("x", xmin + i*topicScale).attr("y", ymax).attr("transform", "rotate(45, " + (xmin + i*topicScale) + ", " + ymax + ")").html(getShortTopic(topics[i]));
		var vertop = $("<text></text>").addClass("t1").attr("x", xmin + i*topicScale).attr("y", (ymin-topicScale)).attr("transform", "rotate(-45, " + (xmin + i*topicScale) + ", " + (ymin-topicScale) + ")").html(getShortTopic(topics[i]));
		graph.append(hor);
		graph.append(ver);
		graph.append(vertop);
	}
	
	for(var t1=0; t1 < numtopics-1; t1++) {
		for(var t2=t1+1; t2 < numtopics; t2++) {
			var val = corrlation_table[t1][t2];
			var r = circleScale(Math.abs(val));
			var color = val > 0 ? "#88f" : "#f88";
			var circle = $("<circle></circle>").attr("cx", xmin + t1*topicScale).attr("cy", ymin + t2*topicScale).attr("r", r).css("fill", color);
			var circle2 = $("<circle></circle>").attr("cx", xmin + t2*topicScale).attr("cy", ymin + t1*topicScale).attr("r", r).css("fill", color);
			var cover = $("<circle></circle>").addClass("cover").attr("cx", xmin + t1*topicScale).attr("cy", ymin + t2*topicScale).attr("r", topicScale/3).attr("title", splitTopicToLines(topics[t1], 5, ", ") + ' /<br>' + splitTopicToLines(topics[t2], 5, ", ")).attr("data-t1", t1).attr("data-t2", t2);
			var cover2 = $("<circle></circle>").addClass("cover").attr("cx", xmin + t2*topicScale).attr("cy", ymin + t1*topicScale).attr("r", topicScale/3).attr("title", splitTopicToLines(topics[t2], 5, ", ") + ' /<br>' + splitTopicToLines(topics[t1], 5, ", ")).attr("data-t1", t2).attr("data-t2", t1);;
			graph.append(circle);
			graph.append(circle2);
			graph.append(cover);
			graph.append(cover2);
		}
	}
	process.stdout.write("done\n");
	return JSON.stringify($("<div></div>").append(graph).html());
}

// preprocess documents
process.stdout.write("processing documents...\n")
var documents = docfile.split("\n");
documents.splice(documents.length-1, 1); // remove empty line added by script
if(numdocs !== documents.length) {process.stderr.write("[Error] document count mismatch: " + numdocs + ' vs. ' + documents.length);}
var doc_table = [];

var firstM = 99999;
var lastM = 0;

documents.forEach(function(element, index, array) {
	var e = element.split("\t");
	var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
	if(isNaN(Date.parse(e[1]))) { // no date given from csv
		// try to find date in url instead
		var l = e[0];
		var m = l.match("20[0-9][0-9]/(?:0?[0-9]|1[0-2])/(?:0?[0-9]|[1-2][0-9]|3[0-1]])");
		if( m != null ) { // year, month, and day
			var d = new Date(Date.parse(m[0]));
			var dn = d.getFullYear()*12+d.getMonth();
			doc_table[index] = {link: e[0], date: months[d.getMonth()] + " " +  d.getDate() + ", " + d.getFullYear(), content: e[2], datenum: dn};
			firstM = dn < firstM ? dn : firstM;
			lastM = dn > lastM ? dn : lastM;
			return;
		}
		m = l.match("20[0-9][0-9]/(?:0?[0-9]|1[0-2])");
		if( m != null ) { // year and month only
			var d = new Date(Date.parse(m[0]));
			var mon = d.getMonth() + 1;
			var dn = d.getFullYear()*12+d.getMonth();
			doc_table[index] = {link: e[0], date: months[d.getMonth()] + " ??, " + d.getFullYear(), content: e[2], datenum: dn};
			firstM = dn < firstM ? dn : firstM;
			lastM = dn > lastM ? dn : lastM;
			return;
		}
		m = l.match("20[0-9][0-9]");
		if( m != null ) { // year only
			var d = new Date(Date.parse(m[0]));
			doc_table[index] = {link: e[0], date: "??? ??, " + d.getFullYear(), content: e[2], datenum: -1};
			return;
		}
		doc_table[index] = {link: e[0], date: "??? ??, ????", content: e[2], datenum: -1};
	} else { // use date given
		var d = new Date(Date.parse(e[1]));
		var dn = d.getFullYear()*12+d.getMonth();
		doc_table[index] = {link: e[0], date: months[d.getMonth()] + " " +  d.getDate() + ", " + d.getFullYear(), content: e[2], datenum: dn};
		firstM = dn < firstM ? dn : firstM;
		lastM = dn > lastM ? dn : lastM;
	}
	
});

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

function getTimeSeriesGraphHtml() {
	process.stdout.write("generating time series graph...");
	var h = 110;
	var w = 500;
	var months = lastM - firstM + 1;
	var w1 = w/2/months;
	var result = $("<div></div>");
	var topavg = 0;
	var topdocs = 0;
	var data = {valavg: [], numdocs: []};
	
	var totdocs = new Array(months);
	for(var t=0; t<months; t++) {totdocs[t] = 0;}
	doc_table.forEach(function(doc) {
		if(doc.datenum < 0) {return;}
		var month = doc.datenum-firstM;
		totdocs[month]++;
	});
	totdocs.forEach(function(n){
		topdocs = n > topdocs ? n : topdocs;
	});
	
	for(var topic=0; topic < numtopics; topic++) {
		var valtotal = new Array(months);
		var valtotal1 = new Array(months);
		var docs1 = new Array(months);
		var docs2 = new Array(months);
		var docs3 = new Array(months);
		var docs4 = new Array(months);
		
		var valavg = new Array(months);
		var valavg1 = new Array(months);
		
		for(var t=0; t<months; t++) {
			valtotal[t] = 0;
			valtotal1[t] = 0;
			
			docs1[t] = 0;
			docs2[t] = 0;
			docs3[t] = 0;
			docs4[t] = 0;
		}
		var valrow = sorted_topic_table[topic];
		var docrow = sorted_topic_docid[topic];
		for(var i=0; i<valrow.length; i++) {
			var doc = doc_table[docrow[i]];
			if(doc.datenum < 0) {continue;}
			var month = doc.datenum-firstM;
			var val = valrow[i];
			valtotal[month] += val;
			if(val > 0.5) {
				docs1[month]++;
			} 
			if(val > 0.25) {
				docs2[month]++;
			}
			if(val > 0.1) {
				docs3[month]++;
			}
			if(val > 0.01){
				valtotal1[month] += val;
				docs4[month]++;
			}
		}
		var mostdocs = 0;
		var bestavg = 0;
		for(var i=0; i<months; i++) {
			if (totdocs[i] > 0) {
				valavg[i] = totdocs[i] == 0 ? 0: valtotal[i]/totdocs[i];
				valavg1[i] = docs4[i] == 0 ? 0 : valtotal1[i]/docs4[i];
				mostdocs = docs4[i] > mostdocs ? docs4[i] : mostdocs;
				bestavg = valavg[i] > bestavg ? valavg[i] : bestavg;
				bestavg = valavg1[i] > bestavg ? valavg1[i] : bestavg;
				topavg = bestavg > topavg ? bestavg : topavg;
			}
		}
		data.valavg.push({all: valavg, one: valavg1});
		data.numdocs.push({dt: totdocs, d1: docs1, d2: docs2, d3: docs3, d4: docs4});
		{
			var d = "0,0";
			var d0 = "0,0"
			for(var i=0; i<months; i++) {
				var h1 = (100*valavg[i]/bestavg);
				d+=" " + (i*w1) + "," + h1;
				h1 = (100*valavg1[i]/bestavg);
				d0+=" " + (i*w1) + "," + h1;
			}
			d+=" " + ((months-1)*w1) + ",0";
			d0+=" " + ((months-1)*w1) + ",0";
			var div = $("<div></div>").addClass("ts-div").addClass("valavg").attr("data-tid", topic).attr("data-h", bestavg).attr("data-w", (months-1)*w1);
			var svg = $("<svg></svg>").attr("width", w).attr("height", h).attr("viewBox", "0 0 " + ((months-1)*w1) + " 100").attr("preserveAspectRatio", "none");
			var g = $("<g></g>");
			var path = $("<polyline></polyline>").attr("points", d).addClass("avgall");
			var path0 = $("<polyline></polyline>").attr("points", d0).addClass("avgone");
			var text = $("<text></text>").html("<br>&nbsp;"+topics[topic]);
			var scale = $("<text></text>").html((bestavg*100).toFixed(1) + "%").addClass("avgscale");			
			g.append(path0).append(path);
			svg.append(g);
			div.append(scale);
			div.append(text);
			div.append(svg)
			result.append(div);
		}
		{
			var d1 = "0,0";
			var d2 = "0,0";
			var d3 = "0,0";
			var d4 = "0,0";
			var dz = "0,0";
			for(var i=0; i<months; i++) {
				var ph;
				ph = (100*docs1[i]/mostdocs);
				d1+=" " + (i*w1) + "," + ph;
				ph = (100*docs2[i]/mostdocs);
				d2+=" " + (i*w1) + "," + ph;
				ph = (100*docs3[i]/mostdocs);
				d3+=" " + (i*w1) + "," + ph;
				ph = (100*docs4[i]/mostdocs);
				d4+=" " + (i*w1) + "," + ph;
				ph = (100*totdocs[i]/mostdocs);
				dz+=" " + (i*w1) + "," + ph;
			}
			d1+=" " + ((months-1)*w1) + ",0";
			d2+=" " + ((months-1)*w1) + ",0";
			d3+=" " + ((months-1)*w1) + ",0";
			d4+=" " + ((months-1)*w1) + ",0";
			dz+=" " + ((months-1)*w1) + ",0";
			var div = $("<div></div>").addClass("ts-div").addClass("numdocs").attr("data-tid", topic).attr("data-h", mostdocs).attr("data-w", (months-1)*w1);
			var svg = $("<svg></svg>").attr("width", w).attr("height", h).attr("viewBox", "0 0 " + ((months-1)*w1) + " 100").attr("preserveAspectRatio", "none");
			var g = $("<g></g>");
			var path1 = $("<polyline></polyline>").attr("points", d1).addClass("p1");
			var path2 = $("<polyline></polyline>").attr("points", d2).addClass("p2");
			var path3 = $("<polyline></polyline>").attr("points", d3).addClass("p3");
			var path4 = $("<polyline></polyline>").attr("points", d4).addClass("p4");
			var pathz = $("<polyline></polyline>").attr("points", dz).addClass("pz");
			var text = $("<text></text>").html("<br>&nbsp;"+topics[topic]);
			var scale = $("<text></text>").html(mostdocs).addClass("numscale");
			g.append(pathz).append(path4).append(path3).append(path2).append(path1);
			svg.append(g);
			div.append(scale);
			div.append(text);
			div.append(svg)
			result.append(div);
		}
	}
	result.children(".ts-div.valavg").attr("data-h0", topavg);
	result.children(".ts-div.numdocs").attr("data-h0", topdocs);
	process.stdout.write("done\n");
	return JSON.stringify({data: data, graph: result.html()});
}

process.stdout.write("preprocessing html...");
const pagesize = 40; // number of documents on one page
const maxpage = Math.floor(numdocs/pagesize+1);
var homepageHtml = pp.preprocess(html, {TOPICS: topic_dom.html(), DOCS: getDocumentsHtml(0, 0, pagesize), MAXPAGE: maxpage, MINM: firstM, MAXM: lastM});
process.stdout.write("done\n");

// package necessary data for server to run
// Note: function cannot be packaged so needs to be sync-ed manually
process.stdout.write("dumping data to file...\n");
var nodeLDA = {};
nodeLDA.numtopics = numtopics; // number of topics
nodeLDA.numdocs = numdocs; // number of document
nodeLDA.pagesize = pagesize; // number of documents in a page
nodeLDA.maxpage = maxpage; // maximum number of pages
nodeLDA.homepageHtml = homepageHtml; // the html preprocessed with some additional data
nodeLDA.doc_table = doc_table; // the documents and its data
nodeLDA.sorted_topic_docid = sorted_topic_docid; // document id sorted by values for each topic
nodeLDA.sorted_topic_table = sorted_topic_table; // values sorted for each topic
nodeLDA.correlation_graph = getCorrelationGraphHtml(); // the correlation graph html the server sends upon request
nodeLDA.time_series_graph = getTimeSeriesGraphHtml(); // the time series graph html the server sends upon request
nodeLDA.topic_table_diag = topic_table_diag; // values in the order of the documents for each topic
nodeLDA.topic_prob = topic_prob; // number of documents that is higher than the cutoff value for each topic
nodeLDA.topics = topics; // the list of topics

fs.writeFileSync("nodeLDA.json", JSON.stringify(nodeLDA), {encoding: 'utf8'});