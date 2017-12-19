// Content Script:
// This file is injected into the current tab. It will allow us to make modifications
// to the existing HTML on the user's current page. We need this to do the highlighting and
// annotations, which cannot be done from popup.js.

// Altered versions of indexOf and lastIndexOf are from SO:
// https://stackoverflow.com/questions/273789/is-there-a-version-of-javascripts-string-indexof-that-allows-for-regular-expr
String.prototype.regexIndexOf = function(regex, startpos) {
    var indexOf = this.substring(startpos || 0).search(regex);
    return (indexOf >= 0) ? (indexOf + (startpos || 0)) : indexOf;
};

String.prototype.regexLastIndexOf = function(regex, startpos) {
    regex = (regex.global) ? regex : new RegExp(regex.source, "g" + (regex.ignoreCase ? "i" : "") + (regex.multiLine ? "m" : ""));
    if(typeof (startpos) == "undefined") {
        startpos = this.length;
    } else if(startpos < 0) {
        startpos = 0;
    }
    var stringToWorkWith = this.substring(0, startpos + 1);
    var lastIndexOf = -1;
    var nextStop = 0;
    while((result = regex.exec(stringToWorkWith)) != null) {
        lastIndexOf = result.index;
        regex.lastIndex = ++nextStop;
    }
    return lastIndexOf;
};

// Define the dictionary of colors used for each frame:
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

// Listener for upcoming port connections attempted by popup.js processes. Handles annotations.
chrome.runtime.onConnect.addListener(function(port){
    port.onMessage.addListener(function(msg) {
        if (msg.f >= 0 && msg.f < 15) {
            var ret = highlight(msg.sentence, colors[msg.f]);
            port.postMessage({status: ret});
        }
        else {
            styleMe("red");
        }
    });
});

// A quickly-identifiable method of error testing. When receiving an invalid message from popup.js,
// it will color the entire webpage red as a warning. This should obviously be removed from any non-dev
// versions of this, but it's helpful when testing for errors and correctness.
function styleMe(color)
{
    document.body.style.backgroundColor = color;
}

// Given a sentence (what) and a color, does the annotations desired. It's extremely complicated and
// got way out of hand to work, but for a basic rundown of what's happening here:
// - first, search for the innermost node with matching innerText for the sentence given
// - identify the sentence in the HTML element and separate it from other sentences or tags
// - handle cases where the HTML has no formatting (HTML tags) within the sentence
// - handle cases where there is HTML in the sentence (ie: an a tag for a link)
// - finally, edit the HTML and update the HTML element on the webpage
// One other thing to note is that I found at one point that the annotation process was causing a race
// condition while making edits. This was because at first, the annotations were so easy and quick that
// they'd be editing the same HTML at practically the same time. After a lot of testing since then, it doesn't
// seem like this happens anymore, but it's worth keeping in mind.
function highlight(what, color) {
    //console.log("starting highlight()");
    //var allNodes = document.body.querySelectorAll("p");
    var desiredNode = null;
    var idx = -1;
    var innerHtmlString, innerTextString;
    var tmp;
    var selectionLength = what.length;
    console.log("WHAT:");
    console.log(what);

    // Find desired article text within the body of the page. Gradually determine the lowest level
    // node possible to do alterations to.
    var newDesiredNode;
    desiredNode = document.body;
    while (desiredNode.innerText.indexOf(what) >= 0)
    {
        var childrenOfDN = desiredNode.children;
        if (childrenOfDN.length === 0)
        {
            //alert("element has no children; exiting");
            break;
        }
        else
        {
            //console.log("children length: " + childrenOfDN.length.toString());
            newDesiredNode = null;
            for (var j = 0; j < childrenOfDN.length; j++)
            {
                //alert("child node: " + childrenOfDN[j].innerText);
                if (childrenOfDN[j].innerText) {
                    //alert("whoa");
                    if (childrenOfDN[j].innerText.indexOf(what) >= 0) {
                        console.log("child not undefined");
                        newDesiredNode = childrenOfDN[j];
                        break;
                    }
                }
            }
            if (newDesiredNode === null) {  // it's only non-null if it changed; otherwise, it didn't change
                //alert("no more sub-nodes that match, our deepest find is: " + desiredNode.innerText);
                break;
            }
            else {
                //alert("sub-node found!");
                desiredNode = newDesiredNode;
            }
        }
    }

    var beforeSelection, afterSelection, selectionItself;

    // NOTE: If we've reached this conditional, we know it's in this element somewhere, otherwise we would've
    // returned with a console-bound error message. It's either easy to detect or a total pain.
    if (desiredNode.innerHTML.indexOf(what) >= 0) // this is ideal: means there's no weird html formatting in sentence!
    {
        idx = desiredNode.innerHTML.indexOf(what); // (try to avoid race condition here in case that's happening)
        console.log("Simple find, no weird formatting issues.");
        beforeSelection = desiredNode.innerHTML.substring(0,idx-1);
        afterSelection = desiredNode.innerHTML.substring(idx+selectionLength);
        selectionItself = desiredNode.innerHTML.substring(idx,idx+selectionLength);

        // Now change the element's innerHTML:
        desiredNode.innerHTML = beforeSelection + " <span style='background-color: " + color + "'>" + selectionItself + "</span>" + afterSelection;
        return "ok";
    }
    else    // oh boy, there's some weird reformatting ahead...
    {
        console.log("Complex find, weird formatting issues must be worked around.");
        // Let's build a regex search string for detecting where the sentence starts in the innerHTML.

        // By replacing spaces with any character and searching this, we will be able to just ignore any
        // HTML tags directly next to or even separate from the rest of the desired sentence.
        // NOTE: If there's an article with a repeated sentence in the same element, there could be some weird
        // behavior. I have no idea how to resolve this at the moment, but the user would still get the same
        // output and be able to determine both sentence's frames since they will be identical anyway, so it's
        // more a stylistic issue than anything else.
        var whatWithNewDelimiter = what.replace(/\./g,"\\.");
        whatWithNewDelimiter = whatWithNewDelimiter.replace(/\(/g,"\\(");
        whatWithNewDelimiter = whatWithNewDelimiter.replace(/\)/g,"\\)");
        whatWithNewDelimiter = whatWithNewDelimiter.replace(/[\s:“”‘’]+/g, "(.*?)");
        whatWithNewDelimiter = whatWithNewDelimiter.replace(/\[/g,"\\[");
        whatWithNewDelimiter = whatWithNewDelimiter.replace(/]/g,"\\]");
        whatWithNewDelimiter = whatWithNewDelimiter.replace(/\//g,"\\/");
        //whatWithNewDelimiter = whatWithNewDelimiter.replace(/“/g,"\\“");
        //whatWithNewDelimiter = whatWithNewDelimiter.replace(/:/g,"\\:");
        //whatWithNewDelimiter = whatWithNewDelimiter.replace(/\-/g,"\\-/");
        //console.log(whatWithNewDelimiter);
        var startIndex = desiredNode.innerHTML.toString().regexIndexOf(whatWithNewDelimiter);
        // endIndex should be startIndex + the length of the group(0) retrieved by the regex search!
        //var endIndex = desiredNode.innerHTML.toString().regexLastIndexOf(whatWithNewDelimiter);
        whatWithNewDelimiter = "(" + whatWithNewDelimiter + ")";
        var regexWWND = new RegExp(whatWithNewDelimiter);
        var desiredNodeText = desiredNode.innerHTML.toString();
        var match = desiredNodeText.match(regexWWND);
        //console.log(match.length.toString());
        // console.log("match[0]: " + match[0].toString());
        // console.log("match[1]: " + match[1].toString());
        var endIndex = match[0].length + startIndex;
        // console.log("match[1] length: " + match[1].length.toString());
        //console.log("start index: " + startIndex.toString());
        //console.log("end index: " + endIndex.toString());
        beforeSelection = desiredNode.innerHTML.substring(0,startIndex);
        afterSelection = desiredNode.innerHTML.substring(endIndex);
        selectionItself = desiredNode.innerHTML.substring(startIndex, endIndex);


        var containsAnySubtag = /(<(\/)?([A-Za-z]*)( ([A-Za-z]+=.*?)*)?>)/;
        var containsSubtags;
        //var myMatch;
        var span = "<span style='background-color: " + color + "'>", endSpan = "</span>";
        var fixedSelection = "";
        var foundSpan = false, foundMyOwnTag = false, adjustTracking = false;
        var matchIndex, lengthOfSelection, myOwnTags;

        // make sure to skip ahead of any tagging I already did to different sections to prevent it from
        // painting over sections I already worked on
        //<span style='background-color: #F00000'>
        var myTag = /<span style=['"]background-color: #[A-F0-9]{1,6}['"]>/;
        //console.log("SELECTION ITSELF BEFORE CHECKING: " + selectionItself);
        while ((myOwnTags = selectionItself.match(myTag)) !== null)
        {
            //console.log("Found another of my annotations, attempting to circumvent it: " + selectionItself);
            matchIndex = selectionItself.search(myTag);
            lengthOfSelection = myOwnTags[0].length;
            fixedSelection += selectionItself.substring(0, matchIndex+lengthOfSelection);
            selectionItself = selectionItself.substring(matchIndex+lengthOfSelection);
            adjustTracking = true;
            //console.log("Updated fixedSelection: " + fixedSelection);
        }
        if (adjustTracking === true)
        {
            myOwnTags = selectionItself.match(/<\/span>/);
            //console.log("Finishing up skipping my own annotations." + selectionItself);
            matchIndex = selectionItself.search(/<\/span>/);
            lengthOfSelection = myOwnTags[0].length;
            fixedSelection += selectionItself.substring(0, matchIndex+lengthOfSelection);
            selectionItself = selectionItself.substring(matchIndex+lengthOfSelection);
        }

        fixedSelection += span;
        while ((containsSubtags = selectionItself.match(containsAnySubtag)) !== null)  // means there's a subtag still in there
        {
            //console.log("SELECTION ITSELF: " + selectionItself);
            matchIndex = selectionItself.search(containsAnySubtag);
            lengthOfSelection = containsSubtags[0].length;

            if (containsSubtags[3] === "span" && containsSubtags[2] === "")
            {
                foundSpan = true;
                fixedSelection += endSpan + selectionItself.substring(0, matchIndex+lengthOfSelection);
            }
            else if (containsSubtags[3] === "span" && containsSubtags[2] === "/")
            {
                foundSpan = false;
                fixedSelection += selectionItself.substring(0, matchIndex+lengthOfSelection) + span;
            }
            else if (foundSpan === false && matchIndex !== 0)
            {
                fixedSelection += selectionItself.substring(0,matchIndex) + endSpan +
                    selectionItself.substring(matchIndex, matchIndex+lengthOfSelection) + span;
            }
            else if (foundSpan === false)
            {
                fixedSelection += endSpan + selectionItself.substring(0, matchIndex+lengthOfSelection) + span;
            }


            //console.log("MATCH 0: " + containsSubtags[0]);
            //console.log("MATCH 1: " + containsSubtags[1]);

            // placeholder
            if (containsSubtags[3] === "script" || containsSubtags[3] === "style")
            {
                console.log("script/style found!");
            }

            selectionItself = selectionItself.substring(matchIndex+lengthOfSelection);
            //console.log("CURRENT FINAL SELECTION: " + fixedSelection);
        }

        if (foundSpan === false)
        {
            fixedSelection += selectionItself + endSpan; // need to close it at the end there.
        }
        else
        {
            fixedSelection += selectionItself;  // need to close it without a span closer.
        }

        //console.log("FINAL INSIDE OF SELECTION: " + fixedSelection);
        //console.log("BEFORE SELECTION: " + beforeSelection);
        desiredNode.innerHTML = beforeSelection + fixedSelection + afterSelection;
        //console.log("FINISHED PRODUCT: " + desiredNode.innerHTML);
        return "ok";
    }
}
