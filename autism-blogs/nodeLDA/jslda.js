"use strict";
// tab switch
$("#docs-tab").click(function() {
  $(".page").css("display", "none");
  $(".tabs ul li").attr("class", "");
  $("#docs-page").css("display", "block");
  $("#docs-tab").attr("class", "selected");
});
$("#corr-tab").click(function() {
  $(".page").css("display", "none");
  $(".tabs ul li").attr("class", "");
  $("#corr-page").css("display", "block");
  $("#corr-tab").attr("class", "selected");
});
$("#ts-tab").click(function() {
  $(".page").css("display", "none");
  $(".tabs ul li").attr("class", "");
  $("#ts-page").css("display", "block");
  $("#ts-tab").attr("class", "selected");
});
$("#help-tab").click(function() {
  $(".page").css("display", "none");
  $(".tabs ul li").attr("class", "");
  $("#help-page").css("display", "block");
  $("#help-tab").attr("class", "selected");
});

// topic list
$("#topics .topicwords").each(function(index) {$(this).data("topic-id", index);});
var currtopic = 0;
$("#topics .topicwords").click(function(){
	var topic = $(this);
	if(topic.hasClass("selected")) { return; }
	$("#topics .topicwords.selected").removeClass("selected");
	topic.addClass("selected");
    $.ajax({
        type: "GET",
        url: "/",
        data: $.param({tid: topic.data("topic-id")}),
        dataType: "json",
        success: function(data) {
			var old = $("#docs-page .document");
			old.last().after(data.html);
			old.remove();
			currtopic = topic.data("topic-id");
			currpage = 1;
			$(".dest").val("");
			$(".curr").html(data.page);
			checkFirstPage();
			checkLastPage();
			$("#docs-tab").click(); // go to docs tab
		}
    });
});

// docs tab
var currpage = 1;
var maxpage = $(".dest").first().data('maxpage');
$(".dest").first().removeData('maxpage');
$(".dest").attr("min", 1);
$(".dest").attr("max", maxpage);
if (maxpage == 1) {
	$(".dest").css("display", "none");
	$(".go").css("display", "none");
	$(".prev").css("display", "none");
	$(".next").css("display", "none");
} else {
	$(".dest").attr("placeholder", "1~" + maxpage);
}
function checkFirstPage() {
	if(currpage == 1) {
		$(".prev").css("visibility", "hidden");
		$(".next").css("visibility", "");
	} else {
		$(".prev").css("visibility", "");
	}
};
checkFirstPage();
function checkLastPage() {
	if(currpage == maxpage) {
		$(".prev").css("visibility", "");
		$(".next").css("visibility", "hidden");
	} else {
		$(".next").css("visibility", "");
	}
}

$(".prev").click(function(){
	$.ajax({
        type: "GET",
        url: "/",
        data: $.param({tid: currtopic, page: currpage-1}),
        dataType: "json",
        success: function(data) {
			var old = $("#docs-page .document");
			old.last().after(data.html);
			old.remove();
			currpage = parseInt(data.page);
			$(".dest").val("");
			$(".curr").html(data.page);
			checkFirstPage();
			checkLastPage();
		}
    });
});

$(".next").click(function(){
	$.ajax({
        type: "GET",
        url: "/",
        data: $.param({tid: currtopic, page: currpage+1}),
        dataType: "json",
        success: function(data) {
			var old = $("#docs-page .document");
			old.last().after(data.html);
			old.remove();
			currpage = parseInt(data.page);
			$(".dest").val("");
			$(".curr").html(data.page);
			checkFirstPage();
			checkLastPage();
		}
    });
});

$(".dest").keypress(function(evt){
	if(evt.which == 13) { // enter key
		evt.preventDefault();
		var page = parseInt($(this).val());
		if(isNaN(page)) {$(".dest").val(""); return;}
		$.ajax({
			type: "GET",
			url: "/",
			data: $.param({tid: currtopic, page: page}),
			dataType: "json",
			success: function(data) {
				var old = $("#docs-page .document");
				old.last().after(data.html);
				old.remove();
				currpage = parseInt(data.page);
				$(".dest").val("");
				$(".curr").html(data.page);
				checkFirstPage();
				checkLastPage();
			}
		});
	}
});

$(".go").click(function(){
	var page = parseInt($(this).prev(".dest").val());
	if(isNaN(page)) {$(".dest").val(""); return;}
	$.ajax({
        type: "GET",
        url: "/",
        data: $.param({tid: currtopic, page: page}),
        dataType: "json",
        success: function(data) {
			var old = $("#docs-page .document");
			old.last().after(data.html);
			old.remove();
			currpage = parseInt(data.page);
			$(".dest").val("");
			$(".curr").html(data.page);
			checkFirstPage();
			checkLastPage();
		}
    });
});

// topic toggle
$("#hide-topic").click(function(){
	$("#show-topic").css("display", "");
	$(this).css("display", "none");
	$(".sidebar").css("display", "none");
	$("#pages").css("margin-left", "0%");
});

$("#show-topic").click(function(){
	$("#hide-topic").css("display", "");
	$(this).css("display", "none");
	$(".sidebar").css("display", "");
	$("#pages").css("margin-left", "22%");
});

// corr tab
$.ajax({
    type: "GET",
    url: "/cgraph",
    dataType: "json",
    success: function(data) {
		$("#cgraph").after(data).remove();
		$("#corr-page circle.cover").each(function() {
			var circle = $(this);
			var t1 = circle.data("t1");
			var t2 = circle.data("t2");
			circle.removeAttr("data-t1");
			circle.removeAttr("data-t2");
			circle.data("t1", t1);
			circle.data("t2", t2);
			
			var title = circle.attr("title");
			circle.removeAttr("title");
			circle.mouseover(function(evt) {
				var tooltip = $("#tooltip");
				tooltip.html($("<span></span>").css("font-size", "small").html(title));
				tooltip.css("visibility", "visible").css("top", evt.pageY + 10);
				var left = evt.pageX - $("#tooltip").width() - 20;
				tooltip.css("left", left < 0 ? 0 : left);
			});
			circle.mouseout(function() {
				$("#tooltip").css("visibility", "hidden");
			});
			circle.click(function(){
				$.ajax({
					type: "GET",
					url: "/corr",
					data: $.param({t1: circle.data("t1"), t2: circle.data("t2")}),
					dataType: "json",
					success: function(data) {
						$(".corr-zoom-graph").remove();
						$("#corr-page").append($("<div></div>").addClass("corr-zoom-graph").append(data.graph));
						$(".corr-zoom-graph").append($("<div></div>").addClass("viewer").css("display", "none"));
						$(".viewer").append($("<div></div>").css("margin", "auto").css("width", "80%")
							.append($("<div></div>").addClass("border1"))
							.append($("<div></div>").addClass("border2"))
							.append($("<div></div>").addClass("docviewer"))
							.append($("<div></div>").addClass("border3"))
							.append($("<div></div>").addClass("border4")));
						$(".viewer").append($("<div></div>").html("^").css("margin", "auto").css("width", 25).css("text-align", "center")
						.css("border", "2px solid #ccc").css("background", "#fff").css("cursor", "pointer")
						.click(function(){
							$(".corr-zoom-graph .top, .corr-zoom-graph .bot").remove();
							$(".corr-zoom-graph .viewer").animate({height: "hide"});
							$(".corr-zoom-graph svg").children().removeClass("chosen");
							$(".corr-zoom-graph svg").removeData("selected");
						}));
						$(".corr-zoom-graph").append($("<div></div>").addClass("close").html("X").click(function(){$(".corr-zoom-graph").remove();}));
						var xmin = parseInt($(".corr-zoom-graph svg").attr("viewBox").split(" ")[0]);
						var svgw = $(".corr-zoom-graph svg").width(); 
						var xmap = new Array($(".corr-zoom-graph svg").children().length);
						$(".corr-zoom-graph svg").children().each(function(){
							var index = $(this).data("index");
							$(this).removeAttr("data-index");
							$(this).data("index", index);
							var x = $(this).attr("x") ? parseFloat($(this).attr("x")) + 0.5 : $(this).attr("cx");
							xmap[index] = {x: (x-xmin)/(xmin*-2)*svgw, obj: $(this)};
						});
						
						var hoverIndex = 0;
						$(".corr-zoom-graph svg").mousemove(function(evt) {
							var x = evt.offsetX;
							var diff = svgw;
							for(var i=0; i<xmap.length; i++) {
								var dx = Math.abs(x - xmap[i].x);
								if(dx > diff) {
									break;
								} else {
									diff = dx;
									hoverIndex = i;
								}
							}
							$(".corr-zoom-graph svg").children().removeClass("peek");
							xmap[hoverIndex].obj.addClass("peek");
							
							var numdocs = data.cumlen[hoverIndex] - (hoverIndex == 0 ? 0 : data.cumlen[hoverIndex-1]);
							var tooltip = $("#tooltip");
							tooltip.html(numdocs + " document" + (numdocs > 1 ? "s" : ""));
							tooltip.css("visibility", "visible").css("top", evt.pageY + 10);
							var left = evt.pageX - $("#tooltip").width() - 20;
							tooltip.css("left", left < 0 ? 0 : left);
						}).mouseout(function(){
							$(".corr-zoom-graph svg").children().removeClass("peek");
							$("#tooltip").css("visibility", "hidden");
						}).click(function(){
							getCorrDocs(hoverIndex);
						});
						var getCorrDocs = function(index) {
							$(".corr-zoom-graph svg").data("selected", index);
							$(".corr-zoom-graph .top, .corr-zoom-graph .bot").remove();
							var left = xmap[index].x + $(".corr-zoom-graph svg").offset().left - parseFloat($(".corr-zoom-graph").css("margin-left"));
							var dtop = $("<div></div>").addClass("top").css("top", 10).css("left", left).css("z-index", 2).css("color", "#0cc").html("▼");	
							var dbot = $("<div></div>").addClass("bot").css("bottom", 10).css("left", left).css("z-index", 2).css("color", "#0cc").html("▲");
							$(".corr-zoom-graph").append(dtop).append(dbot);
							$(".corr-zoom-graph .top, .corr-zoom-graph .bot").each(function(){$(this).css("left", parseFloat($(this).css("left")) - $(this).width()/2);});
							$(".corr-zoom-graph .viewer").animate({height: "show"});
							$(".corr-zoom-graph .docviewer").html("");
							
							$(".corr-zoom-graph svg").children().removeClass("chosen");
							xmap[index].obj.addClass("chosen");
							
							var start = index == 0 ? 0 : data.cumlen[index-1];
							$.ajax({
								type: "GET",
								url: "/corrdocs",
								data: {t1: circle.data("t1"), t2: circle.data("t2"), docids: data.docids.slice(start, data.cumlen[index])},
								success: function(docs) {
									$(".corr-zoom-graph .docviewer").html(docs);
								}
							});
						}
						$(".corr-zoom-graph .left").click(function(){
							var index = $(".corr-zoom-graph svg").data("selected");
							if(typeof index == "undefined") { return; }
							if(index > 0) {
								getCorrDocs(--index);
							}
						});
						$(".corr-zoom-graph .right").click(function(){
							var index = $(".corr-zoom-graph svg").data("selected");
							if(typeof index == "undefined") { return; }
							if(index < xmap.length-1) {
								getCorrDocs(++index);
							}
						});
					}
				});
			});
			
		});
		// zoom feature for correlation graph
		var corr_ratio = 1.0;
		var corr_width = $("#corr-page svg").width();
		var corr_height = $("#corr-page svg").height();
		$("#corr-zoom-in").click(function(){
			corr_ratio += 0.1;
			$("#corr-page svg").attr("width", (corr_width*corr_ratio).toFixed(0));
			$("#corr-page svg").attr("height", (corr_height*corr_ratio).toFixed(0));
		});
		$("#corr-zoom-one").click(function(){
			corr_ratio = 1.0;
			$("#corr-page svg").attr("width", corr_width);
			$("#corr-page svg").attr("height", corr_height);
		});
		$("#corr-zoom-out").click(function(){
			if(corr_ratio < 0.2) {return;}
			corr_ratio -= 0.1;
			$("#corr-page svg").attr("width", (corr_width*corr_ratio).toFixed(0));
			$("#corr-page svg").attr("height", (corr_height*corr_ratio).toFixed(0));
		});
	}
});

// ts tab
$.ajax({
    type: "GET",
    url: "/tgraph",
    dataType: "json",
    success: function(obj) {
		$("#tgraph").after(obj.graph).remove();
		
		// dimention variables
		var tsRatio = 1.0;
		var tsWidth = $(".ts-div svg").width();
		var tsHeight = $(".ts-div svg").height();
		var ts_text_h = parseInt($(".ts-div text").css("top"));
		var ts_text_w = parseInt($(".ts-div text").css("left"));
		
		const viewWidth = 310;
		var viewHeight = 101;
		const viewHeight2 = 101;
		var viewRatio = 1.0;
		var viewRatio2 = 1.0;
		const viewXmin = 5;
		var viewYmin = -0.5;
		const viewYmin2 = -0.5;
		var viewX = viewXmin;
		var viewY = viewYmin;
		var viewX2 = viewXmin;
		var viewY2 = viewYmin2;
		
		$("#ts-page").mouseup(function(){
			$(".ts-zoom-graph svg, .ts-zoom-graph2 svg").data("drag", false);
		});

		var temp = [-0.25, 0, 0.25];
		var offset = [0, -0.25, 0.25];
		for(var i=0; i<5; i++) {
			var l = temp.length;
			var temp2 = [];
			for(var j=0; j<l-1; j++) {
				temp.push((temp[j]+temp[j+1])/2);
				temp2.push((temp[j]+temp[j+1])/2);
			}
			var temp3 = 0;
			while(temp2.length > 0) {
				offset.push(temp2.splice(temp3, 1)[0]);
				temp3 = temp3 == 0 ? temp2.length - 1 : 0;
			}
			temp.sort(function(a, b) {return a-b;});
		}
		
		var addZoomGraphListeners = function(arr) {
			var shiftgraph = function(svg, ptx, pty, relx, rely, scaleshift) {
				var w = viewWidth * viewRatio;
				var h = viewHeight * viewRatio;

				viewX = ptx-relx*w;
				viewY = pty-rely*h;

				viewX = viewX < viewXmin ? viewXmin : viewX;
				viewX = viewX + w > viewWidth + viewXmin ? viewWidth + viewXmin - w : viewX;
				viewY = viewY < viewYmin ? viewYmin: viewY;
				viewY = viewY + h > viewHeight + viewYmin ? viewHeight + viewYmin - h : viewY;
				if(scaleshift) {
					$(".ts-zoom-graph svg ellipse").attr("rx", viewWidth/tsWidth*(1-(1-viewRatio)/1.2)).attr("ry" , viewHeight/tsHeight*(1-(1-viewRatio)/1.2));
				}
				svg.setAttribute("viewBox", viewX + " "+ viewY + " " + w + " " + h);
				$(".ts-zoom-graph .scales .top-scale").html((viewY + viewHeight*viewRatio).toFixed(1) + "σ");
				if(viewY > 0 || viewY + viewHeight*viewRatio < 0) {
					$(".ts-zoom-graph .scales .mid-scale").html("");
				} else {
					$(".ts-zoom-graph .scales .mid-scale").html("avg");
					$(".ts-zoom-graph .scales .mid-scale").css("top", (1+(viewY/viewHeight/viewRatio))*100 + "%");
				}
				$(".ts-zoom-graph .scales .bot-scale").html((viewY).toFixed(1) + "σ");
				addDayScale();
			}
			
			$(".ts-zoom-graph svg").off("mousedown");
			$(".ts-zoom-graph svg").mousedown(function(evt){
				$(this).data("drag", true);
				$(this).data("ptx", viewX + evt.offsetX*viewRatio*viewWidth/$(this).width());
				$(this).data("pty", viewY + evt.offsetY*viewRatio*viewHeight/$(this).height());
			});
			$(".ts-zoom-graph svg").off("mousemove");
			$(".ts-zoom-graph svg").mousemove(function(evt){
				if($(this).data("drag")) {
					var ptx = $(this).data("ptx");
					var pty = $(this).data("pty");
					var relx = evt.offsetX/$(this).width();
					var rely = evt.offsetY/$(this).height();
					shiftgraph(this, ptx, pty, relx, rely, false);
				}
			});

			$(".ts-zoom-graph svg").off("mousewheel");
			$(".ts-zoom-graph svg").off("DOMMouseScroll");
			$(".ts-zoom-graph svg").bind('mousewheel DOMMouseScroll', function(evt){
				evt.preventDefault();
				var ptx = viewX + evt.offsetX*viewRatio*viewWidth/$(this).width();
				var pty = viewY + evt.offsetY*viewRatio*viewHeight/$(this).height();
				var relx = evt.offsetX/$(this).width();
				var rely = evt.offsetY/$(this).height();
				if (evt.originalEvent.wheelDelta > 0 || evt.originalEvent.detail < 0) { // zoom in
					viewRatio = viewRatio.toFixed(1) <= 0.1 ? 0.1 : viewRatio - 0.05;
				} else { //  zoom out
					viewRatio = viewRatio.toFixed(1) >= 1 ? 1 : viewRatio + 0.05;
				}
				shiftgraph(this, ptx, pty, relx, rely, true);
			});
			$(".ts-zoom-graph .prev-month, .ts-zoom-graph .next-month").off("click");
			$(".ts-zoom-graph .prev-month, .ts-zoom-graph .next-month").click(function() {
				var m = $(this).data("m");
				getZoomGraph($(this).data("tid"), m, arr);
			});
			$(".ts-zoom-graph .close").off("click");
			$(".ts-zoom-graph .close").click(function(){
				$(".ts-zoom-graph").not("#ts-zoom-div .ts-zoom-graph").remove();
				$(".ts-div.valavg.display-none").removeClass("display-none");
			});
			
		}
		var addZoomGraphListeners2 = function() {
			var shiftgraph2 = function(svg, ptx, pty, relx, rely, scaleshift) {
				var w = viewWidth * viewRatio2;
				var h = viewHeight2 * viewRatio2;
				
				viewX2 = ptx-relx*w;
				viewY2 = pty-rely*h;

				viewX2 = viewX2 < viewXmin ? viewXmin : viewX2;
				viewX2 = viewX2 + w > viewWidth + viewXmin ? viewWidth + viewXmin - w : viewX2;
				viewY2 = viewY2< viewYmin2 ? viewYmin2 : viewY2;
				viewY2 = viewY2 + h > viewHeight2 + viewYmin2 ? viewHeight2 + viewYmin2 - h : viewY2;
				if(scaleshift) {
					$(".ts-zoom-graph2 svg ellipse").attr("rx", viewWidth/tsWidth*(1-(1-viewRatio2)/1.2)).attr("ry" , viewHeight2/tsHeight*(1-(1-viewRatio2)/1.2));
				}
				svg.setAttribute("viewBox", viewX2 + " " + viewY2 + " " + w + " " + h);
				$(".ts-zoom-graph2 .scales .top-scale").html(Math.floor(viewY2 + h) + "%");
				$(".ts-zoom-graph2 .scales .mid-scale").html(Math.round(viewY2 + h/2) + "%");
				$(".ts-zoom-graph2 .scales .bot-scale").html(Math.ceil(viewY2) + "%");
				addDayScale2();
			}
			
			$(".ts-zoom-graph2 svg").off("mousedown");
			$(".ts-zoom-graph2 svg").mousedown(function(evt){
				$(this).data("drag", true);
				$(this).data("ptx", viewX2 + (evt.offsetX*viewRatio2*viewWidth/$(this).width()));
				$(this).data("pty", viewY2 + (evt.offsetY*viewRatio2*viewHeight2/$(this).height()));
			});
			$(".ts-zoom-graph2 svg").off("mousemove");
			$(".ts-zoom-graph2 svg").mousemove(function(evt){
				if($(this).data("drag")) {
					var ptx = $(this).data("ptx");
					var pty = $(this).data("pty");
					var relx = evt.offsetX/$(this).width();
					var rely = evt.offsetY/$(this).height();
					shiftgraph2(this, ptx, pty, relx, rely, false);
				}
			});
			
			$(".ts-zoom-graph2 svg").off("mousewheel");
			$(".ts-zoom-graph2 svg").off("DOMMouseScroll");
			$(".ts-zoom-graph2 svg").bind('mousewheel DOMMouseScroll', function(evt){
				evt.preventDefault();
				var ptx = viewX2 + (evt.offsetX*viewRatio2*viewWidth/$(this).width());
				var pty = viewY2 + (evt.offsetY*viewRatio2*viewHeight2/$(this).height());
				var relx = evt.offsetX/$(this).width();
				var rely = evt.offsetY/$(this).height();
				
				if (evt.originalEvent.wheelDelta > 0 || evt.originalEvent.detail < 0) { // zoom in
					viewRatio2 = viewRatio2.toFixed(1) <= 0.1 ? 0.1 : viewRatio2 - 0.05;
				} else { // zoom out
					viewRatio2 = viewRatio2.toFixed(1) >= 1 ? 1 : viewRatio2 + 0.05;
				}
				
				shiftgraph2(this, ptx, pty, relx, rely, true);
			});
			$(".ts-zoom-graph2 .prev-month, .ts-zoom-graph2 .next-month").off("click");
			$(".ts-zoom-graph2 .prev-month, .ts-zoom-graph2 .next-month").click(function() {
				var m = $(this).data("m");
				getZoomGraph2($(this).data("tid"), m);
			});
			$(".ts-zoom-graph2 .close").off("click");
			$(".ts-zoom-graph2 .close").click(function(){
				$(".ts-zoom-graph2").not("#ts-zoom-div2 .ts-zoom-graph2").remove();
				$(".ts-div.numdocs.display-none").removeClass("display-none");
			});
			
		}
		
		var addTSGraphListener = function(graph, tid, topic, arr){
			graph.click(function(evt){
				var width = $(this).width();
				var index = Math.round(evt.offsetX/width*(maxMonth-minMonth));
				var m = minMonth + index;
				$(".ts-div.valavg.display-none").removeClass("display-none");
				$(".ts-zoom-graph").not("#ts-zoom-div .ts-zoom-graph").remove();
				$(".ts-zoom-graph .scales .topic").html(topic);
				graph.after($("#ts-zoom-div").html());
				graph.addClass("display-none");
				getZoomGraph(tid, m, arr);
			});
		}
		var addTSGraphListener2 = function(graph, tid, topic){
			graph.click(function(evt){
				var width = $(this).width();
				var index = Math.round(evt.offsetX/width*(maxMonth-minMonth));
				var m = minMonth + index;
				$(".ts-div.numdocs.display-none").removeClass("display-none");
				$(".ts-zoom-graph2").not("#ts-zoom-div2 .ts-zoom-graph2").remove();
				$(".ts-zoom-graph2 .scales .topic").html(topic);
				graph.after($("#ts-zoom-div2").html());
				graph.addClass("display-none");
				viewRatio2 = 1.0;
				$(".ts-zoom-graph2 svg").each(function(){this.setAttribute("viewBox", viewXmin + " " + viewYmin2 + " " + viewWidth + " " +viewHeight2)});
				$(".ts-zoom-graph2 .scales .top-scale").html("100%");
				$(".ts-zoom-graph2 .scales .mid-scale").html("50%");
				$(".ts-zoom-graph2 .scales .bot-scale").html("0%");
				getZoomGraph2(tid, m);
				addZoomGraphListeners2();
			});
		}
		
		var getZoomGraph = function(tid, m, arr) {
			var avg = arr[m-minMonth]; 
			$(".ts-zoom-graph span").html(toMonth(m));
			$(".ts-zoom-graph svg").html("");
			addDayScale();
			$(".ts-zoom-graph .prev-month").data("tid", tid);
			$(".ts-zoom-graph .next-month").data("tid", tid);
			$(".ts-zoom-graph .prev-month").data("m", m-1);
			$(".ts-zoom-graph .next-month").data("m", m+1);
			$(".ts-zoom-graph .prev-month").css("visibility", $(".ts-zoom-graph .prev-month").data("m") < minMonth ? "hidden" : "");
			$(".ts-zoom-graph .next-month").css("visibility", $(".ts-zoom-graph .next-month").data("m") > maxMonth ? "hidden" : "");
			$.ajax({
				type: "GET",
				url: "/tgraph",
				data: $.param({tid: tid, month: m}),
				dataType: "json",
				success: function(obj) {
					viewRatio = 1.0;
					var lastY = -10;
					const nudgeLimit = viewHeight2/tsHeight/1.2;
					var day = 1;
					var idx = 0;
					var max = 0;
					var min = 0;
					
					var sameday = [];
					var normalize = function(){
						if(sameday.length != 0) {
							var dayavg = sameday.reduce(function(dayavg, el){ return dayavg + parseFloat(el.attr("cy")) }, 0);
							dayavg /= sameday.length;
							var daydiff = sameday.map(function(el){ var diff = parseFloat(el.attr("cy")) - dayavg; return diff * diff; });
							daydiff = daydiff.reduce(function(daydiff, val){ return daydiff + val; }, 0);
							daydiff /= sameday.length;
							var daystd = Math.sqrt(daydiff);
							
							daystd = daystd == 0 ? 1 : daystd; 
							for(var j=0; j<sameday.length; j++) {
								var e = sameday[j];
								var cy = parseFloat(e.attr("cy"));
								cy = parseFloat(((cy - dayavg) / daystd).toFixed(3));
								
								max = cy > max ? cy : max;
								min = cy < min ? cy : min;
								$(".ts-zoom-graph svg").append(e.attr("cy", cy));
							}
							sameday = [];
						}
					}
					for(var i=0; i<obj.length; i++) {
						var p = obj[i];
						if(day !== p.x) {
							lastY = -10;
							idx = 0;
							day = p.x;
							normalize();
						}
						if(p.y - lastY > nudgeLimit/100) {
							lastY = p.y;
							idx = 0;
						}
						var temp = $("<ellipse></ellipse>").attr("cx", ((p.x+offset[idx])*10).toFixed(3)).attr("cy", (p.y*100)).attr("data-tooltip", p.html);
						temp.addClass("avgone");
						sameday.push(temp);
						idx = (idx+1)%offset.length;
					}
					normalize();
					
					max += 0.1;
					min -= 0.1;
					viewYmin = min;
					viewHeight = max - min;
					
					if(viewHeight <= 0.4) {
						for(var i=1; i<31; i++) {
							$(".ts-zoom-graph svg").append($("<line></line>").attr("stroke-dasharray", "0.01, 0.01").attr("x1", (i+0.5)*10).attr("x2", (i+0.5)*10).attr("y1", (viewYmin-1)).attr("y2", (viewYmin+viewHeight+1)).css("stroke-width", 0.2).css("stroke", "#555"));
						}
					} else {
						for(var i=1; i<31; i++) {
							$(".ts-zoom-graph svg").append($("<line></line>").attr("stroke-dasharray", "0.1, 0.1").attr("x1", (i+0.5)*10).attr("x2", (i+0.5)*10).attr("y1", (viewYmin-1)).attr("y2", (viewYmin+viewHeight+1)).css("stroke-width", 0.2).css("stroke", "#555"));
						}
					}
					
					$(".ts-zoom-graph svg").append($("<line></line>").attr("stroke-dasharray", "1, 1").attr("x1", (viewXmin-1)).attr("x2", (viewXmin+viewWidth+1)).attr("y1", 0).attr("y2", 0).css("stroke-width", 0.4*viewHeight/viewHeight2).css("stroke", "#f00"));
					for(var i=Math.floor(min); i<=Math.ceil(max); i++) {
						if(i == 0) {continue;}
						$(".ts-zoom-graph svg").append($("<line></line>").attr("stroke-dasharray", "1, 1").attr("x1", (viewXmin-1)).attr("x2", (viewXmin+viewWidth+1)).attr("y1", i).attr("y2", i).css("stroke-width", 0.4*viewHeight/viewHeight2).css("stroke", "#555"));
					}

					$(".ts-zoom-graph svg").each(function(){this.setAttribute("viewBox", viewXmin + " " + viewYmin + " " + viewWidth + " " + viewHeight);});
					$(".ts-zoom-graph svg ellipse").attr("rx", viewWidth/tsWidth*(1-(1-viewRatio)/1.2)).attr("ry" , viewHeight/tsHeight*(1-(1-viewRatio)/1.2));
					
					$(".ts-zoom-graph .scales .top-scale").html(max.toFixed(1) + "σ");
					$(".ts-zoom-graph .scales .mid-scale").html("avg");
					$(".ts-zoom-graph .scales .mid-scale").css("top", (1+(min/(max-min)))*100 + "%");
					$(".ts-zoom-graph .scales .bot-scale").html(min.toFixed(1) + "σ");
					
					$(".ts-zoom-graph svg").html($(".ts-zoom-graph svg").html());
					$(".ts-zoom-graph svg ellipse").each(function(){
						var tooltip = $(this).data("tooltip");
						$(this).removeAttr("data-tooltip");
						$(this).data("tooltip", tooltip);
					});
					$(".ts-zoom-graph svg ellipse").mouseover(function(evt){
						$("#tooltip").html($(this).data("tooltip")).addClass("ts-tooltip");
						$("#tooltip .document").prepend(parseFloat($(this).attr("cy")).toFixed(2) + "σ")
						$("#tooltip").css("visibility", "visible").css("top", evt.pageY + 10).css("left", evt.pageX + (evt.pageX > $(window).width()/2 ? - $("#tooltip").width()-20 : 20));
					}).mouseout(function() {
						$("#tooltip").css("visibility", "hidden").removeClass("ts-tooltip");
					}).click(function() {
						window.open($("#tooltip a").attr("href"));
					});
					
					addZoomGraphListeners(arr);
				}
			});
		}
		
		var getZoomGraph2 = function(tid, m) {
			$(".ts-zoom-graph2 span").html(toMonth(m));
			$(".ts-zoom-graph2 svg").html("");
			addDayScale2();
			$(".ts-zoom-graph2 .prev-month").data("tid", tid);
			$(".ts-zoom-graph2 .next-month").data("tid", tid);
			$(".ts-zoom-graph2 .prev-month").data("m", m-1);
			$(".ts-zoom-graph2 .next-month").data("m", m+1);
			$(".ts-zoom-graph2 .prev-month").css("visibility", $(".ts-zoom-graph2 .prev-month").data("m") < minMonth ? "hidden" : "");
			$(".ts-zoom-graph2 .next-month").css("visibility", $(".ts-zoom-graph2 .next-month").data("m") > maxMonth ? "hidden" : "");
			$.ajax({
				type: "GET",
				url: "/tgraph",
				data: $.param({tid: tid, month: m}),
				dataType: "json",
				success: function(obj) {
					for(var i=1; i<31; i++) {
						$(".ts-zoom-graph2 svg").append($("<line></line>").attr("stroke-dasharray", "1, 1").attr("x1", (i+0.5)*10).attr("x2", (i+0.5)*10).attr("y1", (viewYmin2-1)).attr("y2", (viewYmin2+viewHeight2+1)).css("stroke-width", 0.1).css("stroke", "#555"));
					}
					for(var i=1; i<10; i++) {
						$(".ts-zoom-graph2 svg").append($("<line></line>").attr("stroke-dasharray", "1, 1").attr("x1", (viewXmin-1)).attr("x2", (viewXmin+viewWidth-1)).attr("y1", i*10).attr("y2", i*10).css("stroke-width", 0.1).css("stroke", "#555"));
					}
					var lastY = -10;
					const nudgeLimit = viewHeight2/tsHeight/1.2;
					var day = 1;
					var idx = 0;
					for(var i=0; i<obj.length; i++) {
						var p = obj[i];
						if(day !== p.x) {
							lastY = -10;
							idx = 0;
							day = p.x;
						}
						if(p.y - lastY > nudgeLimit/100) {
							lastY = p.y;
							idx = 0;
						}
						var temp = $("<ellipse></ellipse>").attr("rx", viewWidth/tsWidth*(1-(1-viewRatio2)/1.2)).attr("ry", viewHeight2/tsHeight*(1-(1-viewRatio2)/1.2)).attr("cx", ((p.x+offset[idx])*10).toFixed(3)).attr("cy", (p.y*100).toFixed(3)).attr("data-tooltip", p.html);
						if(p.y > 0.5) {
							temp.addClass("p1");
						} else if(p.y > 0.25) {
							temp.addClass("p2");
						} else if(p.y > 0.05) {
							temp.addClass("p3");
						} else if(p.y > 0.01) {
							temp.addClass("p4");
						} else {
							temp.addClass("pz");
						}
						$(".ts-zoom-graph2 svg").append(temp);
						idx = (idx+1)%offset.length;
					}
					$(".ts-zoom-graph2 svg").html($(".ts-zoom-graph2 svg").html());
					$(".ts-zoom-graph2 svg ellipse").each(function(){
						var tooltip = $(this).data("tooltip");
						$(this).removeAttr("data-tooltip");
						$(this).data("tooltip", tooltip);
					});
					$(".ts-zoom-graph2 svg ellipse").mouseover(function(evt){
						$("#tooltip").html($(this).data("tooltip")).addClass("ts-tooltip");
						$("#tooltip .document").prepend(parseFloat($(this).attr("cy")).toFixed(1) + "%");
						$("#tooltip").css("visibility", "visible").css("top", evt.pageY + 10).css("left", evt.pageX + (evt.pageX > $(window).width()/2 ? -$("#tooltip").width()-40 : 20));
					}).mouseout(function() {
						$("#tooltip").css("visibility", "hidden").removeClass("ts-tooltip");
					}).click(function() {
						window.open($("#tooltip a").attr("href"));
					});
				}
			});
		}
		
		var addDayScale = function() {
			$(".ts-zoom-graph .scales .day").remove();
			var Xmin = Math.ceil(viewX /10);
			var Xmax = Math.floor((viewX + viewWidth*viewRatio)/10);
			for(var i = Xmin; i <= Xmax; i++) {
				$(".ts-zoom-graph .scales").append($("<text></text>").addClass("day").html(i).css("left", (-(viewX-i*10)*($(".ts-zoom-graph svg").width()/viewWidth/viewRatio))).css("bottom", -13));
			}
			$(".ts-zoom-graph .scales .day").each(function(){
				$(this).css("left", parseFloat($(this).css("left"))-$(this).width()/2);
			});
		}
		var addDayScale2 = function() {
			$(".ts-zoom-graph2 .scales .day").remove();
			var Xmin = Math.ceil(viewX2/10);
			var Xmax = Math.floor((viewX2 + viewWidth*viewRatio2)/10);
			for(var i = Xmin; i <= Xmax; i++) {
				$(".ts-zoom-graph2 .scales").append($("<text></text>").addClass("day").html(i).css("left", (-(viewX2-i*10)*($(".ts-zoom-graph2 svg").width()/viewWidth/viewRatio2))).css("bottom", -13));
			}
			$(".ts-zoom-graph2 .scales .day").each(function(){
				$(this).css("left", parseFloat($(this).css("left"))-$(this).width()/2);
			});
		}

		var minMonth = $("#ts-page").data("minmonth");
		var maxMonth = $("#ts-page").data("maxmonth");
		$("#ts-page").removeAttr("data-minmonth");
		$("#ts-page").removeAttr("data-maxmonth");
		function toMonth(num) {
			var names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
			var m = num%12;
			return names[m] + ", " + Math.floor(num/12);
		}
		// mouseover info display
		$(".ts-div.valavg").each(function() {
			var graph = $(this);
			var tid = graph.data("tid");
			graph.removeAttr("data-tid");
			var arr = obj.data.valavg[tid];
			graph.mousemove(function(evt) {
				var width = $(this).width();
				var index = Math.round(evt.offsetX/width*(maxMonth-minMonth));
				var m = minMonth + index;
				$("#tooltip").html(toMonth(m))
					.append($("<br>")).append($("<span></span>").css("color", "#ff8f00").html("average (>1%) : " + (arr.one[index]*100).toFixed(1) + "%"))
					.append($("<br>")).append($("<span></span>").css("color", "#ffb600").html("average (all)&emsp;: " + (arr.all[index]*100).toFixed(1) + "%"));
				$("#tooltip").css("visibility", "visible").css("top", evt.pageY).css("left", evt.pageX + (evt.pageX > $(window).width()/2 ? -$("#tooltip").width()-40 : 20) );
			});
			graph.mouseout(function() {
				$("#tooltip").css("visibility", "hidden");
			});
			addTSGraphListener(graph, tid, graph.children("text").not(".avgscale").html(), arr.one);
		});
		$(".ts-div.numdocs").each(function() {
			var graph = $(this);
			var tid = graph.data("tid");
			graph.removeAttr("data-tid");
			var arr = obj.data.numdocs[tid];
			graph.mousemove(function(evt) {
				var width = $(this).width();
				var index = Math.round(evt.offsetX/width*(maxMonth-minMonth));
				var m = minMonth + index;
				$("#tooltip").html(toMonth(m))
					.append($("<br>")).append($("<span></span>").css("color", "#999").html("out of: " + arr.dt[index]))
					.append($("<br>")).append($("<span></span>").css("color", "#64b5f6").html(">01% : " + arr.d4[index]))
					.append($("<br>")).append($("<span></span>").css("color", "#2196f3").html(">10% : " + arr.d3[index]))
					.append($("<br>")).append($("<span></span>").css("color", "#1976d2").html(">25% : " + arr.d2[index]))
					.append($("<br>")).append($("<span></span>").css("color", "#0d47a1").html(">50% : " + arr.d1[index]));
				$("#tooltip").css("visibility", "visible").css("top", evt.pageY).css("left", evt.pageX + (evt.pageX > $(window).width()/2 ? -$("#tooltip").width()-40 : 20) );
			});
			graph.mouseout(function() {
				$("#tooltip").css("visibility", "hidden");
			});
			addTSGraphListener2(graph, tid, graph.children("text").not(".numscale").html());
		});
		
		// zoom feature for svgs
		$(".ts-zoom-graph svg").attr("width", tsWidth).attr("height", tsHeight);
		$(".ts-zoom-graph2 svg").attr("width", tsWidth).attr("height", tsHeight);
		$(".ts-zoom-graph svg")[0].setAttribute("viewBox", viewXmin + " " + viewYmin2 + " " + viewWidth + " " + viewHeight2);
		$(".ts-zoom-graph2 svg")[0].setAttribute("viewBox", viewXmin + " " + viewYmin2 + " " + viewWidth + " " + viewHeight2);
		$("#ts-zoom-in").click(function(){
			tsRatio += 0.1;
			$(".ts-div svg").attr("width", (tsWidth*tsRatio).toFixed(0));
			$(".ts-div svg").attr("height", (tsHeight*tsRatio).toFixed(0));
			$(".ts-div text").css("left", (ts_text_w*tsRatio).toFixed(2));
			$(".ts-div text").css("top", (ts_text_h*tsRatio).toFixed(2));
			$(".ts-div text").css("font-size", tsRatio*100 + "%");
			$(".ts-zoom-graph svg").attr("width", (tsWidth*tsRatio).toFixed(0)).attr("height", (tsHeight*tsRatio).toFixed(0));
			$(".ts-zoom-graph2 svg").attr("width", (tsWidth*tsRatio).toFixed(0)).attr("height", (tsHeight*tsRatio).toFixed(0));
			addDayScale();
			addDayScale2();
		});
		$("#ts-zoom-one").click(function(){
			tsRatio = 1.0;
			$(".ts-div svg").attr("width", tsWidth);
			$(".ts-div svg").attr("height", tsHeight);
			$(".ts-div text").css("left", ts_text_w);
			$(".ts-div text").css("top", ts_text_h);
			$(".ts-div text").css("font-size", "100%");
			$(".ts-zoom-graph svg").attr("width", tsWidth).attr("height", tsHeight);
			$(".ts-zoom-graph2 svg").attr("width", tsWidth).attr("height", tsHeight);
			addDayScale();
			addDayScale2();
		});
		$("#ts-zoom-out").click(function(){
			if(tsRatio < 0.2) {return;}
			tsRatio -= 0.1;
			$(".ts-div svg").attr("width", (tsWidth*tsRatio).toFixed(0));
			$(".ts-div svg").attr("height", (tsHeight*tsRatio).toFixed(0));
			$(".ts-div text").css("left", (ts_text_w*tsRatio).toFixed(2));
			$(".ts-div text").css("top", (ts_text_h*tsRatio).toFixed(2));
			$(".ts-div text").css("font-size", tsRatio*100 + "%");
			$(".ts-zoom-graph svg").attr("width", (tsWidth*tsRatio).toFixed(0)).attr("height", (tsHeight*tsRatio).toFixed(0));
			$(".ts-zoom-graph2 svg").attr("width", (tsWidth*tsRatio).toFixed(0)).attr("height", (tsHeight*tsRatio).toFixed(0));
			addDayScale();
			addDayScale2();
		});
		// scaling with corpus
		$(".ts-div").each(function(){
			var div = $(this);
			var h0 = div.data("h0");
			var h = div.data("h");
			var w = div.data("w");
			div.removeAttr("data-h0");
			div.removeAttr("data-h");
			div.removeAttr("data-w");
			div.data("w", w);
			div.data("h", h);
			div.data("h0", h0);
		});
		$("#ts-scale-corpus").click(function(){
			$(".ts-div").each(function(){
				var div = $(this);
				div.children(".avgscale").html((div.data("h0")*100).toFixed(1)+"%");
				div.children(".numscale").html(div.data("h0"));
				var svg = div.children("svg");
				var hmin = (div.data("h0")/div.data("h")*100);
				svg.attr("viewBox", "0 0 " + div.data("w") + " " + hmin);
			});
		});
		$("#ts-scale-topic").click(function(){
			$(".ts-div").each(function(){
				var div = $(this);
				div.children(".avgscale").html((div.data("h")*100).toFixed(1)+"%");
				div.children(".numscale").html(div.data("h"));
				var svg = div.children("svg");
				svg.attr("viewBox", "0 0 " + div.data("w") + " 100");
			});
		});
		// checkbox
		$("#cbox-valavg").click(function(){
			if($(this).prop("checked")) {
				$(".ts-div.valavg").css("display", "");
				$(".ts-zoom-graph").not("#ts-zoom-div .ts-zoom-graph").css("display", "");
			} else {
				$(".ts-div.valavg").css("display", "none");
				$(".ts-zoom-graph").not("#ts-zoom-div .ts-zoom-graph").css("display", "none");
			}
		});
		$("#cbox-numdocs").click(function(){
			if($(this).prop("checked")) {
				$(".ts-div.numdocs").css("display", "");
				$(".ts-zoom-graph2").not("#ts-zoom-div2 .ts-zoom-graph2").css("display", "");
			} else {
				$(".ts-div.numdocs").css("display", "none");
				$(".ts-zoom-graph2").not("#ts-zoom-div2 .ts-zoom-graph2").css("display", "none");
			}
		});
	}
});