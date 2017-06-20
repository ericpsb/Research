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

// corr tab
$("#corr-page circle").each(function() {
	var circle = $(this);
	var tooltip = circle.attr("title");
	circle.attr("title", "");
	circle.mouseover(function(evt) {
		$("#tooltip").html(tooltip).css("visibility", "visible").css("top", evt.pageY - 65).css("left", evt.pageX - $("#tooltip").width()/1.25);
	});
	circle.mouseout(function() {
		$("#tooltip").css("visibility", "hidden");
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

// ts tab
var minMonth = $("#ts-page").data("minmonth");
var maxMonth = $("#ts-page").data("maxmonth");
function toMonth(num) {
	var m = num%12 + 1;
	return Math.floor(num/12) + "-" + (m < 10? "0" + m : m);
}
$("#ts-page .help").append("The time range is from " + toMonth(minMonth) + " to " + toMonth(maxMonth) + ".");
$("#ts-page svg").each(function() {
	var graph = $(this);
	graph.mousemove(function(evt) {
		var width = $(this).width();
		var m = minMonth + Math.round(evt.offsetX/width*(maxMonth-minMonth));
		$("#tooltip").html(toMonth(m)).css("visibility", "visible").css("top", evt.pageY - 65).css("left", evt.pageX - $("#tooltip").width()/2);
	});
	graph.mouseout(function() {
		$("#tooltip").css("visibility", "hidden");
	});
});
var ts_ratio = 1.0;
var ts_width = $("#ts-page svg").width();
var ts_height = $("#ts-page svg").height();
$("#ts-zoom-in").click(function(){
	ts_ratio += 0.1;
	$("#ts-page svg").attr("width", (ts_width*ts_ratio).toFixed(2));
	$("#ts-page svg").attr("height", (ts_height*ts_ratio).toFixed(2));
})
$("#ts-zoom-out").click(function(){
	if(ts_ratio < 0.2) {return;}
	ts_ratio -= 0.1;
	$("#ts-page svg").attr("width", (ts_width*ts_ratio).toFixed(2));
	$("#ts-page svg").attr("height", (ts_height*ts_ratio).toFixed(2));
})