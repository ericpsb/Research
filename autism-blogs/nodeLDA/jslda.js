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
    dataType: "html",
    success: function(data) {
		$("#cgraph").after(data).remove();
		
		$("#corr-page circle").each(function() {
			var circle = $(this);
			var tooltip = circle.attr("title");
			circle.removeAttr("title");
			circle.mouseover(function(evt) {
				$("#tooltip").html(tooltip).css("visibility", "visible").css("top", evt.pageY - 65);
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
    success: function(data) {
		$("#tgraph").after(data.graph).remove();

		var minMonth = $("#ts-page").data("minmonth");
		var maxMonth = $("#ts-page").data("maxmonth");
		$("#ts-page").removeAttr("data-minmonth");
		$("#ts-page").removeAttr("data-maxmonth");
		function toMonth(num) {
			var m = num%12 + 1;
			return Math.floor(num/12) + "-" + (m < 10? "0" + m : m);
		}
		$("#ts-page .help").append("The time range is from " + toMonth(minMonth) + " to " + toMonth(maxMonth) + ".");
		// mouseover info display
		$(".ts-div.valavg").each(function() {
			var graph = $(this);
			var tid = graph.data("tid");
			graph.removeAttr("data-tid");
			var arr = data.data.valavg[tid];
			graph.mousemove(function(evt) {
				var width = $(this).width();
				var index = Math.round(evt.offsetX/width*(maxMonth-minMonth));
				var m = minMonth + index;
				$("#tooltip").html(toMonth(m)+"<br>average: " + (arr[index]*100).toFixed(1) + "%").css("visibility", "visible").css("top", evt.pageY - 65).css("left", evt.pageX - $("#tooltip").width()/2);
			});
			graph.mouseout(function() {
				$("#tooltip").css("visibility", "hidden");
			});
		});
		$(".ts-div.numdocs").each(function() {
			var graph = $(this);
			var tid = graph.data("tid");
			graph.removeAttr("data-tid");
			var arr = data.data.numdocs[tid];
			graph.mousemove(function(evt) {
				var width = $(this).width();
				var index = Math.round(evt.offsetX/width*(maxMonth-minMonth));
				var m = minMonth + index;
				$("#tooltip").html(toMonth(m)).append($("<br>")).append($("<span></span>").css("color", "#0d47a1").html(">50% : " + arr.d1[index]))
				                              .append($("<br>")).append($("<span></span>").css("color", "#1976d2").html(">25% : " + arr.d2[index]))
											  .append($("<br>")).append($("<span></span>").css("color", "#2196f3").html(">10% : " + arr.d3[index]))
											  .append($("<br>")).append($("<span></span>").css("color", "#64b5f6").html(">1% : " + arr.d4[index]))
											  .append($("<br>")).append($("<span></span>").css("color", "#fff").css("text-shadow", "1px 1px 4px #0d47a1").html("all : " + arr.dt[index]))
				$("#tooltip").css("visibility", "visible").css("top", evt.pageY - 145).css("left", evt.pageX - $("#tooltip").width()/2);
			});
			graph.mouseout(function() {
				$("#tooltip").css("visibility", "hidden");
			});
		});
		// zoom feature for svgs
		var ts_ratio = 1.0;
		var ts_width = $(".ts-div svg").width();
		var ts_height = $(".ts-div svg").height();
		var ts_text_h = parseInt($(".ts-div text").css("top"));
		var ts_text_w = parseInt($(".ts-div text").css("left"));
		$("#ts-zoom-in").click(function(){
			ts_ratio += 0.1;
			$(".ts-div svg").attr("width", (ts_width*ts_ratio).toFixed(0));
			$(".ts-div svg").attr("height", (ts_height*ts_ratio).toFixed(0));
			$(".ts-div text").css("left", (ts_text_w*ts_ratio).toFixed(2));
			$(".ts-div text").css("top", (ts_text_h*ts_ratio).toFixed(2));
			$(".ts-div text").css("font-size", ts_ratio*100 + "%");
		});
		$("#ts-zoom-one").click(function(){
			ts_ratio = 1.0;
			$(".ts-div svg").attr("width", ts_width);
			$(".ts-div svg").attr("height", ts_height);
			$(".ts-div text").css("left", ts_text_w);
			$(".ts-div text").css("top", ts_text_h);
			$(".ts-div text").css("font-size", "100%");
		});
		$("#ts-zoom-out").click(function(){
			if(ts_ratio < 0.2) {return;}
			ts_ratio -= 0.1;
			$(".ts-div svg").attr("width", (ts_width*ts_ratio).toFixed(0));
			$(".ts-div svg").attr("height", (ts_height*ts_ratio).toFixed(0));
			$(".ts-div text").css("left", (ts_text_w*ts_ratio).toFixed(2));
			$(".ts-div text").css("top", (ts_text_h*ts_ratio).toFixed(2));
			$(".ts-div text").css("font-size", ts_ratio*100 + "%");
		});
		// scaling with average value graphs
		$(".ts-div.valavg").each(function(){
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
			$("#ts-scale-topic").css("display", "");
			$(this).css("display", "none");
			$(".ts-div.valavg").each(function(){
				var div = $(this);
				var scale = div.children(".scale");
				var svg = div.children("svg");
				scale.html((div.data("h0")*100).toFixed(0)+"%");
				svg.attr("viewBox", "0 0 " + div.data("w") + " 100");
			});
		});
		$("#ts-scale-topic").click(function(){
			$("#ts-scale-corpus").css("display", "");
			$(this).css("display", "none");
			$(".ts-div.valavg").each(function(){
				var div = $(this);
				var scale = div.children(".scale");
				var svg = div.children("svg");
				scale.html((div.data("h")*100).toFixed(1)+"%");
				var hmin = (div.data("h")/div.data("h0")*100);
				svg.attr("viewBox", "0 " + (100-hmin) + " " + div.data("w") + " " + hmin);
			});
		});
	}
});