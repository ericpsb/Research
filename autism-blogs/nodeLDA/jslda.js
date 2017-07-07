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
			$("#docs-page .document").remove();
			$("#docs-page .help").after(data.html);
			currtopic = topic.data("topic-id");
			currpage = 1;
			$(".dest").val("");
			$(".curr").html(data.page);
			checkFirstPage();
			checkLastPage();
			$("#docs-tab").click();
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
var checkFirstPage = function() {
	if(currpage == 1) {
		$(".prev").css("visibility", "hidden");
		$(".next").css("visibility", "");
	} else {
		$(".prev").css("visibility", "");
	}
};
checkFirstPage();
var checkLastPage = function() {
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
			$("#docs-page .document").remove();
			$("#docs-page .help").after(data.html);
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
			$("#docs-page .document").remove();
			$("#docs-page .help").after(data.html);
			currpage = parseInt(data.page);
			$(".dest").val("");
			$(".curr").html(data.page);
			checkFirstPage();
			checkLastPage();
		}
    });
});

$(".dest").keypress(function(evt){
	if(evt.which == 13) {
		evt.preventDefault();
		var page = parseInt($(this).val());
		if(isNaN(page)) {$(".dest").val(""); return;}
		$.ajax({
			type: "GET",
			url: "/",
			data: $.param({tid: currtopic, page: page}),
			dataType: "json",
			success: function(data) {
				$("#docs-page .document").remove();
				$("#docs-page .help").after(data.html);
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
			$("#docs-page .document").remove();
			$("#docs-page .help").after(data.html);
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
    success: function(obj) {
		$("#cgraph").after(obj.graph).remove();
		
		$("#corr-page circle").each(function() {
			var circle = $(this);
			var t1 = circle.data("t1");
			var t2 = circle.data("t2");
			circle.removeAttr("data-t1");
			circle.removeAttr("data-t2");
			circle.data("t1", t1);
			circle.data("t2", t2);
			var tooltip = circle.attr("title");
			circle.removeAttr("title");
			var big = obj.topic[t1] > obj.topic[t2] ? obj.topic[t1] : obj.topic[t2];
			var small = obj.topic[t1] < obj.topic[t2] ? obj.topic[t1] : obj.topic[t2];
			var intercept = obj.table[t1][t2];
			circle.mouseover(function(evt) {
				$("#tooltip").html($("<span></span>").css("font-size", "small").html(tooltip)).append($("<br>"));
				var svg = $('<svg viewBox="-100 -100 400 200" preserveAspectRatio="none"></svg>').attr("width", 100).attr("height", 50);
				//console.log(obj.topic[t1] + " " + obj.topic[t2] + " " + intercept);
				svg.append($("<circle></circle>").attr("cx", 0).attr("cy", 0).attr("r", Math.round(obj.topic[t1]/big*100)).css("fill", "#f00").css("fill-opacity", 0.5));
				svg.append($("<circle></circle>").attr("cx", ((1+small/big)*100)).attr("cy", 0).attr("r", Math.round(obj.topic[t2]/big*100)).css("fill", "#00f").css("fill-opacity", 0.5));
				$("#tooltip").append(svg);
				$("#tooltip").html($("#tooltip").html());
				$("#tooltip").css("visibility", "visible").css("top", evt.pageY + 10);
				var left = evt.pageX - $("#tooltip").width();
				$("#tooltip").css("left", left < 0 ? 0 : left);
			});
			circle.mouseout(function() {
				$("#tooltip").css("visibility", "hidden");
			});
			
		});

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
		
		var viewWidth = 310;
		var viewHeight = 101;
		var viewRatio = 1.0;
		var viewX = 160;
		var viewY = 50;
		
		var temp = [-0.25, 0, 0.25];
		var offset = [-0.25, 0, 0.25];
		for(var i=0; i<9; i++) {
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
		
		var addZoomGraphListeners = function() {
			$(".ts-zoom-graph svg").mousedown(function(evt){
				evt.preventDefault();
				viewX += (evt.offsetX-$(this).width()/2)*viewRatio;
				viewY += (evt.offsetY-$(this).height()/2)*viewRatio;
				if(evt.which == 1) { // left click zoom in
					viewRatio = viewRatio.toFixed(1) <= 0.1 ? 0.1 : viewRatio - 0.15;
				}else if(evt.which == 3) { // right click zoom out
					viewRatio = viewRatio.toFixed(1) >= 1 ? 1 : viewRatio + 0.15;
				}
				var w = viewWidth * viewRatio;
				var h = viewHeight * viewRatio;
				viewX = viewX - w/2 < 5 ? w/2 + 5 : viewX;
				viewX = viewX + w/2 > viewWidth + 5 ? viewWidth + 5 - w/2 : viewX;
				viewY = viewY - h/2 < -0.5 ? -0.5 + h/2 : viewY;
				viewY = viewY + h/2 > viewHeight - 0.5 ? viewHeight-0.5-h/2 : viewY;
				$(".ts-zoom-graph svg ellipse").attr("rx", viewWidth/tsWidth*(1-(1-viewRatio)/1.2)).attr("ry" , viewHeight/tsHeight*(1-(1-viewRatio)/1.2));
				this.setAttribute("viewBox", (viewX - w/2) + " "+ (viewY - h/2) + " " + w + " " + h);
				$(".ts-zoom-graph .scales .top-scale").html((Math.floor(viewY + h/2)) + "%");
				$(".ts-zoom-graph .scales .bot-scale").html((Math.ceil(viewY - h/2)) + "%");
				$(this).html($(this).html());
				addDayScale();
			});
			$(".ts-zoom-graph .prev-month, .ts-zoom-graph .next-month").click(function() {
				var m = $(this).data("m");
				getZoomGraph($(this).data("tid"), m);
			});
			$(".ts-zoom-graph .close").click(function(){
				$(".ts-zoom-graph").not("#ts-zoom-div .ts-zoom-graph").remove();
				$(".ts-div.display-none").removeClass("display-none");
			});
		}
		var addZoomGraphListener = function(graph, tid, topic){
			graph.click(function(evt){
				var width = $(this).width();
				var index = Math.round(evt.offsetX/width*(maxMonth-minMonth));
				var m = minMonth + index;
				$(".ts-div.display-none").removeClass("display-none");
				$(".ts-zoom-graph").not("#ts-zoom-div .ts-zoom-graph").remove();
				$(".ts-zoom-graph .scales .topic").html(topic);
				graph.after($("#ts-zoom-div").html());
				graph.addClass("display-none");
				getZoomGraph(tid, m);
				addZoomGraphListeners();
			});
		}
		var getZoomGraph = function(tid, m) {
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
					obj.sort(function(a, b) {return a.x == b.x ? a.y - b.y : a.x - b.x;});
					var r = 0.75*320/tsWidth;
					var day = 1;
					var idx = 0;
					for(var i=0; i<obj.length; i++) {
						var p = obj[i];
						idx = day == p.x ? idx : 0;
						day = p.x;
						$(".ts-zoom-graph svg").append($("<ellipse></ellipse>").attr("rx", viewWidth/tsWidth*(1-(1-viewRatio)/1.2)).attr("ry", viewHeight/tsHeight*(1-(1-viewRatio)/1.2)).attr("cx", ((p.x+offset[idx])*10).toFixed(3)).attr("cy", (p.y*100).toFixed(3)));
						idx = (idx+1)%offset.length;
					}
					$(".ts-zoom-graph svg").html($(".ts-zoom-graph svg").html());
				}
			});
		}
		
		var addDayScale = function() {
			$(".ts-zoom-graph .scales .day").remove();
			var Xmin = Math.ceil((viewX - viewWidth*viewRatio/2)/10);
			var Xmax = Math.floor((viewX + viewWidth*viewRatio/2)/10);
			for(var i = Xmin; i <= Xmax; i++) {
				$(".ts-zoom-graph .scales").append($("<text></text>").addClass("day").html(i).css("left", ($(".ts-zoom-graph svg").width()/2-(viewX-i*10)*($(".ts-zoom-graph svg").width()/viewWidth/viewRatio))).css("bottom", -13));
			}
			$(".ts-zoom-graph .scales .day").each(function(){
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
		$("#ts-page .help").append("The time range is from " + toMonth(minMonth) + " to " + toMonth(maxMonth) + ".");
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
			addZoomGraphListener(graph, tid, graph.children("text").not(".avgscale").html());
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
			addZoomGraphListener(graph, tid, graph.children("text").not(".numscale").html());
		});
		
		// zoom feature for svgs
		$(".ts-zoom-graph svg").attr("width", tsWidth).attr("height", tsHeight);
		$("#ts-zoom-in").click(function(){
			tsRatio += 0.1;
			$(".ts-div svg").attr("width", (tsWidth*tsRatio).toFixed(0));
			$(".ts-div svg").attr("height", (tsHeight*tsRatio).toFixed(0));
			$(".ts-div text").css("left", (ts_text_w*tsRatio).toFixed(2));
			$(".ts-div text").css("top", (ts_text_h*tsRatio).toFixed(2));
			$(".ts-div text").css("font-size", tsRatio*100 + "%");
			$(".ts-zoom-graph").css("width", (tsWidth*tsRatio).toFixed(0)).css("height", (tsHeight*tsRatio).toFixed(0));
			$(".ts-zoom-graph svg").attr("width", (tsWidth*tsRatio).toFixed(0)).attr("height", (tsHeight*tsRatio).toFixed(0));
			addDayScale();
		});
		$("#ts-zoom-one").click(function(){
			tsRatio = 1.0;
			$(".ts-div svg").attr("width", tsWidth);
			$(".ts-div svg").attr("height", tsHeight);
			$(".ts-div text").css("left", ts_text_w);
			$(".ts-div text").css("top", ts_text_h);
			$(".ts-div text").css("font-size", "100%");
			$(".ts-zoom-graph").css("width", tsWidth).css("height", tsHeight);
			$(".ts-zoom-graph svg").attr("width", tsWidth).attr("height", tsHeight);
			addDayScale();
		});
		$("#ts-zoom-out").click(function(){
			if(tsRatio < 0.2) {return;}
			tsRatio -= 0.1;
			$(".ts-div svg").attr("width", (tsWidth*tsRatio).toFixed(0));
			$(".ts-div svg").attr("height", (tsHeight*tsRatio).toFixed(0));
			$(".ts-div text").css("left", (ts_text_w*tsRatio).toFixed(2));
			$(".ts-div text").css("top", (ts_text_h*tsRatio).toFixed(2));
			$(".ts-div text").css("font-size", tsRatio*100 + "%");
			$(".ts-zoom-graph").css("width", (tsWidth*tsRatio).toFixed(0)).css("height", (tsHeight*tsRatio).toFixed(0));
			$(".ts-zoom-graph svg").attr("width", (tsWidth*tsRatio).toFixed(0)).attr("height", (tsHeight*tsRatio).toFixed(0));
			addDayScale();
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
			} else {
				$(".ts-div.valavg").css("display", "none");
			}
		});
		$("#cbox-numdocs").click(function(){
			if($(this).prop("checked")) {
				$(".ts-div.numdocs").css("display", "");
			} else {
				$(".ts-div.numdocs").css("display", "none");
			}
		});
	}
});