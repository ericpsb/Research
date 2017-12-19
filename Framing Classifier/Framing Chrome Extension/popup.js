// Left these dictionaries here in case they're useful to have in the future.
// Currently, they're not needed.
var colors = {
    0: "#2F21FF",
    1: "#FFFF00",
    2: "#FF1581",
    3: "#1E030F",
    4: "#F00000",
    5: "#00aeff",
    6: "#1eff1a",
    7: "#ff9999",
    8: "#0a8100",
    9: "#650905",
    10: "#656e85",
    11: "#ff43bb",
    12: "#00ffaa",
    13: "#857dff",
    14: "#433330"
};

var frame_names_dict = {
    f0: "Explicit Anti",
    f1: "Economic primary",
    f2: "Public opinion primary",
    f3: "Morality primary",
    f4: "Policy prescription and evaluation",
    f5: "Capacity and resources",
    f6: "Political headline",
    f7: "Legality, constitutionality, and jurisprudence primary",
    f8: "Fairness and equality",
    f9: "Cultural identity headline",
    f10: "Explicit Pro",
    f11: "Health and safety primary",
    f12: "Morality",
    f13: "Other",
    f14: "External regulation and reputation headline"
};

var tabId = -1;

// Upon loading popup window, set up listener to send article contents to the backend.
chrome.runtime.onMessage.addListener(function(request, sender) {
    if (request.action == "getArticleContent") {    // get article content message
        //message.innerText = request.source;
        prepareJsonPost(request.source);
    }
});

// Runs when popup window is loaded. Gets page source.
function onWindowLoad()
{
    var message = document.querySelector('#message');

    chrome.tabs.executeScript(null, {
        file: "getPagesSource.js"
    }, function() {
        if (chrome.runtime.lastError) {
            message.innerText = 'There was an error injecting script : \n' + chrome.runtime.lastError.message;
        }
    });
}

// Get url and call method to send this info to backend.
function prepareJsonPost(text)
{
    chrome.tabs.query({'active': true, 'lastFocusedWindow': true}, function (tabs) {
        tabId = tabs[0].id;
        sendJsonToFlask(tabs[0].url, text);
    });
}

// Prepare a post to the backend with content and url. Attempt to parse through returned annotations
// after sending the post message.
function sendJsonToFlask(url, text)
{
    var xmlhttp = new XMLHttpRequest();
    xmlhttp.open("POST", "http://127.0.0.1:5000/json");
    xmlhttp.setRequestHeader("Content-Type", "application/json");
    xmlhttp.onload = function () {
        try {
            // SECURITY CONSIDERATION:
            // Note that this sort of message exchange between a base server and
            // an extension leaves users exposed to potential XSS attacks. This issue
            // is mitigated by the fact that the JS JSON.parse() method, which handles
            // the entire serverside response, does not run any code while parsing and
            // should make this response from the server either safe and useful data
            // or content unable to be parsed and, as a result, displays an error.
            var retJsonObj = JSON.parse(xmlhttp.responseText);
        } catch (e) {
            var s = "ERROR: Unable to parse the response as a JSON!";
            console.log(s);
            message.innerText = e.message;
        }

        try {
            xmlProcessReceivedAnnotations(retJsonObj);
        }
        catch (e) {
            var s = "ERROR: Unable to properly handle received annotations!";
            console.log(s);
            message.innerText = e.message;
        }
    };
    xmlhttp.send(JSON.stringify({url: url, content: text}));
}

// Given JSON from Flask, build the popup.html display and communicate with
// content_script.js to annotate the original webpage itself.
function xmlProcessReceivedAnnotations(responseJson)
{
    //alert("starting xmlProcessReceivedAnnotations...");
    message.innerHTML = "<h1>Framing Results:</h1>";//<ul>";
    var sizeOfJson = Object.keys(responseJson).length;
    // we have tabId stored from a previous query

    // This opens a connection with the content script.
    var port = chrome.tabs.connect(tabId, {name: "sendCsMySentences"});
    // port.onMessage.addListener(function (request) {
    //
    //     if (request.status === "ok"){
    //         console.log("Success for sentence!");
    //     }
    //     else{
    //         console.log("Failure for sentence!");
    //     }
    // });

    // For each sentence:
    for (var i = 0; i < sizeOfJson; i++)
    {
        var ctr = (i).toString();
        //message.innerHTML += "<li>" + responseJson[ctr].content + "</li>";

        // Dictionary storing frame values for given sentence:
        var frame_dict = {
            f0: responseJson[ctr].f0,
            f1: responseJson[ctr].f1,
            f2: responseJson[ctr].f2,
            f3: responseJson[ctr].f3,
            f4: responseJson[ctr].f4,
            f5: responseJson[ctr].f5,
            f6: responseJson[ctr].f6,
            f7: responseJson[ctr].f7,
            f8: responseJson[ctr].f8,
            f9: responseJson[ctr].f9,
            f10: responseJson[ctr].f10,
            f11: responseJson[ctr].f11,
            f12: responseJson[ctr].f12,
            f13: responseJson[ctr].f13,
            f14: responseJson[ctr].f14
        };

        var maxKey;
        var maxVal = -1;
        for (var key in frame_dict)         // TODO: Make sure this is even close to right.
        {
            if (frame_dict[key] > maxVal)
            {
                maxKey = key;
                maxVal = frame_dict[key];
            }
        }

        // edit display here:
        var currentCount = parseInt(document.getElementById(maxKey).innerText);
        currentCount += 1;
        document.getElementById(maxKey).innerText = currentCount.toString();

        var maxKeyO = maxKey.substring(1);   // really messy, but for now it's sufficient
        var maxKeyI = parseInt(maxKeyO);
        var currentSentence = responseJson[ctr].content;

        port.postMessage({sentence: currentSentence, f: maxKeyI});
    }

    // Chrome Dev description of using content scripts was pivotal to this implementation:
    // https://developer.chrome.com/extensions/content_scripts

    // TODO: (In Flask) Fix the sentence splitting situation with a sentence splitting API.
    // TODO: Eventually, make the HTML display prettier.
}

// This was originally based on code by Tim Down @ StackOverflow: Original code
// https://stackoverflow.com/questions/5886858/full-text-search-in-html-ignoring-tags
// https://jsfiddle.net/xeSQb/6/
window.onload = onWindowLoad;
