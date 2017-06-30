$(document).ready(function(){
    $("#top5").click(showTopFive);
    $("#closeTopFive").click(closeTopFive);
    $("#popUpVeil").click(closeTopFive);
    $("#post-top-5").click(setUpPost);
    $("#post-to-fb").click(postToFB);

    // get names of top 5
    $.post("topFiveFriends.php", {"name" : main["name"]}, populateTopFive);
});

function showStatus() {
    $("#status").css({opacity: 0.0, visibility: "visible"}).animate({opacity: 1.0});
    window.setTimeout(hideStatus, 3000);
}

function hideStatus() {
    $("#status").css({opacity: 1.0, visibility: "visible"}).animate({opacity: 0.0});
}

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

function postToFB() {
    // post stuff in text area to Facebook with tagged friends
    // check if they are in taggable friends to see if they're actually friends
    $("#post-to-fb").prop("disabled", true);
    $.post("https://das-lab.org/fbprojectb/IDsFromTaggableFriends.php", {
        "username": main["name"],
        "name1": $("#p1-name").text(),
        "name2": $("#p2-name").text(),
        "name3": $("#p3-name").text(),
        "name4": $("#p4-name").text(),
        "name5": $("#p5-name").text()
    }, function(resp) {
        var postURL = "https://graph.facebook.com/v2.9/me/feed";
        var data = {
            "message": $("#post-text").val(),
            "tags": JSON.parse(resp).join(",")
        };

        FB.api(
            "/me/feed",
            "POST",
            data,
            function(resp) {
                $("#post-to-fb").prop("disabled", false);
                if (!resp || resp.error) {
                    console.log(resp); // TODO[P]: better error handling
                }
                else {
                    closeTopFive();
                    showStatus();
                }
            }
        );
    });
}

/* Request and place information for the Top 5 Friends panel */
function populateTopFive(data) {
    // Get names and IDs of top 5
    var parsedData = parseTopFiveData(data);
    var names = [];
    for (var i = 0; i < parsedData.length; i++) {
        names[i] = parsedData[i][0];
    }

    // Fill in text for post to Facebook option
    populateTextArea(names);

    // Get pictures from Graph API and generate items in DOM
    for (var i = 0; i < parsedData.length; i++) {
        generateDivElement(i, names[i], parsedData[i][1]);
    }
}

function populateTextArea(names) {
    $("#post-text").val(getTop5Message(names));
}

function getTop5Message(names) {
    // Note: this makes the assumption that a person has at least five people in the graph
    return "These are my top 5 friends according to TrueFriend!\n" +
           "1. " + names[0] + "\n" +
           "2. " + names[1] + "\n" +
           "3. " + names[2] + "\n" +
           "4. " + names[3] + "\n" +
           "5. " + names[4] + "\n" +
           "Help the Lehigh University DAS Lab, find out your top 5 friends, and see your Social Interaction Graph at https://das-lab.org/fbprojectb !";
}

/* Returns 2d array with first column being names and second column being IDs */
function parseTopFiveData(data) {
    var lines = $.trim(data).split("\n");
    var info = [];
    for (var i = 0; i < lines.length; i++) {
        info[i] = lines[i].split("\t");
    }
    return info;
}

function generateDivElement(index, name, id) {
    var baseURL = "https://graph.facebook.com/v2.9/";
    var fieldsAndAccessToken = "?fields=picture&access_token=" + ac;
    var requestURL = baseURL + id.toString() + fieldsAndAccessToken;

    $.get(requestURL, function(resp) {
        // Place names and images
        var img = document.createElement("img");
        img.src = resp["picture"]["data"]["url"];
        img.alt = "profile picture";
        $("#p" + (index+1) + "-img").append(img);
        $("#p" + (index+1) + "-name").text(name);
    });
}
