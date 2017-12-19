// Adapted from JustRead source: takes in HTML on current page and returns
// the text of the article's content.
function getContainer() {
    var numWordsOnPage = document.body.innerText.match(/\S+/g).length,
        ps = document.body.querySelectorAll("p");

    // Find the paragraphs with the most words in it
    var pWithMostWords = document.body,
        highestWordCount = 0;

    if(ps.length === 0) {
        ps = document.body.querySelectorAll("div");
    }

    for(var i = 0; i < ps.length; i++) {
        // Make sure it's not in our blacklist
        if(checkAgainstBlacklist(ps[i])
            && checkAgainstBlacklist(ps[i].parentNode)) {
            var myInnerText = ps[i].innerText.match(/\S+/g);
            if(myInnerText) {
                var wordCount = myInnerText.length;
                if(wordCount > highestWordCount) {
                    highestWordCount = wordCount;
                    pWithMostWords = ps[i];
                    console.log(checkAgainstBlacklist(ps[i]), checkAgainstBlacklist(ps[i].parentNode))
                }
            }
        }
    }

    // Keep selecting more generally until over 2/5th of the words on the page have been selected
    var selectedContainer = pWithMostWords,
        wordCountSelected = highestWordCount;

    while(wordCountSelected / numWordsOnPage < 0.4
    && selectedContainer != document.body
    && selectedContainer.parentNode.innerText) {
        selectedContainer = selectedContainer.parentNode;
        wordCountSelected = selectedContainer.innerText.match(/\S+/g).length;
    }

    // Make sure a single p tag is not selected
    if(selectedContainer.tagName === "P") {
        selectedContainer = selectedContainer.parentNode;
    }

    // console.log(selectedContainer.className);
    // console.log(selectedContainer.innerHTML);

    return selectedContainer.innerText;
}

// From JustRead source:
// Check given item against blacklist, return null if in blacklist
var blacklist = ["comment"];
function checkAgainstBlacklist(elem) {
    if (typeof elem != "undefined" && elem != null) {
        var className = elem.className;
        for (var i = 0; i < blacklist.length; i++) {
            if (typeof className != "undefined" && className.indexOf(blacklist[i]) >= 0) {
                return null;
            }
        }
    }
    return elem;
}

// After this is computed, send a message as a reply to popup.js with findings.
chrome.runtime.sendMessage({
    action: "getArticleContent",
    source: getContainer()
});
