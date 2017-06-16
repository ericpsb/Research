$(document).ready(function(){
    $("#top5").click(showTopFive);
    $("#closeTopFive").click(closeTopFive);
    $("#popUpVeil").click(closeTopFive);
    $("#post-top-5").click(setUpPost);

    // get names of top 5
    $.post("topFiveFriends.php", {"name" : main["name"]}, populateTopFive);
});

/* Show Top 5 Friends panel */
function showTopFive() {
    $("#popUpVeil").fadeIn();
    $("#topFiveWindow").fadeIn();
}

/* Hide Top 5 Friends panel */
function closeTopFive() {
    $("#topFiveWindow").fadeOut(400, function(){
        $("#top-post").hide();
        $("#panel-1").show();
    });
    $("#popUpVeil").fadeOut();
}

function setUpPost() {
    $("#panel-1").fadeOut(200, function(){
        $("#top-post").fadeIn(200);
    });
}

/* Request and place information for the Top 5 Friends panel */
function populateTopFive(data) {
    // Get names of top 5
    var names = $.trim(data).split("\n");

    // Get pictures from Facebook
    // Requires IDs

    // Place names and images (currently using test data)
    for (var i = 1; i <= 5; i++) {
        var img = document.createElement("img");
        img.src = "https://scontent.xx.fbcdn.net/v/t1.0-1/c15.0.50.50/p50x50/10354686_10150004552801856_220367501106153455_n.jpg?oh=726660dce6ba9660584686ee99a62deb&oe=59D7152F";
        img.alt = "profile picture";
        $("#p" + i + "-img").append(img);
        $("#p" + i + "-name").text(names[i-1]);
    }
}
