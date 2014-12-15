// ==UserScript==
// @name        Highlight_Frame
// @namespace   namespace_Highlight_Frame
// @description This is javascript code that receives data to highlight framing words from an article.
// @include     http://*/*
// @version     1.32
// @grant       none
// @require     http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js
// ==/UserScript==
// var actKey = "";
// var whitelist = "";
// var masterWhiteList = ["www.nytimes.com","junghosohn.com"];
// function save_options() {
//   chrome.storage.sync.set({
//     masterWhiteList: masterWhiteList
//   });
// }
//callback handler for form submit



getLocalStorage(activationFunction);
// chrome.browserAction.setIcon({path:"highlighter.png"});


var doc = document.URL;
var parser = document.createElement('a');
parser.href = doc;
var sourceUrl;

if (parser.protocol == "http:") {
    sourceUrl = parser.hostname;

}

var activation;
var activationKey;
var masterWhiteList;

function getLocalStorage(callback) {
    // Use default value color = 'red' and likesColor = true.
    chrome.storage.sync.get({
        activationKey: "",
        whitelist: "",
        masterWhiteList: ""
    }, function (result) {
        activation = result.activationKey;
        masterWhiteList = result.masterWhiteList;
        callback(activation, masterWhiteList);
    });
}





var $body = $('body');
$body.append('<input type="button" id="annotate" style="visibility:hidden"><input type="button" id="denotate" style="visibility:hidden">');

// add styling to highlight selected frames from browser end
var css = '.highlight { background-color: yellow; white-space:normal; display:inline; } .parent{white-space:normal; display:inline;} .parent .spans{margin:0; padding:0; white-space:normal; display:inline;}',
    head = document.head || document.getElementsByTagName('head')[0],
    style = document.createElement('style');
style.type = 'text/css';
if (style.styleSheet) {
    style.styleSheet.cssText = css;
} else {
    style.appendChild(document.createTextNode(css));
}
head.appendChild(style);

//variable to uniquely identify a highlighted segment
var highlight_index = 0;
var extractedHtmlText = '<HTML xmlns="http://www.w3.org/1999/xhtml">\n<style type="text/css">\nA:before { content:\' \'; } \nA:after { content:\' \'; } \nSPAN:before { content:\' \'; } \nSPAN:after { content:\' \'; } \n</style>\n<BODY><DIV id="content"><DIV class="section"><DIV class="sectionContent"><DIV class="sectionColumns"><DIV class="column1 gridPanel grid8"><H1>Defense chief defends Taliban prisoner swap before Congress</H1><DIV id="articleInfo"><P class="byline">By David Alexander</P></DIV><DIV class="topShare gridPanel grid6"><DIV class="module shareLinks horizontal"><DIV class="moduleBody"><UL><LI tns="no" class="email"><SPAN class="hrefClone" onclick="Reuters.utils.popup(\'/do/emailArticle?articleId=USKBN0EM1KZ20140611\', 580, 735, 1, \'emailArticle\');">Email</SPAN></LI><LI tns="no" class="print last"><SPAN class="hrefClone" onclick="Reuters.utils.popup(\'/assets/print?aid=USKBN0EM1KZ20140611\', 580, 735, 3, \'printArticle\');">Print</SPAN></LI></UL></DIV></DIV></DIV><DIV id="slideshowInlineLarge" style="width: 580px;"><DIV class="rolloverCaption" id="captionContent"><DIV class="rolloverBg"><DIV class="captionText"><P><SPAN class="label">1 of 3. </SPAN>\n                                                U.S. Defense Secretary Chuck Hagel (L) testifies with Defense Department General Counsel Stephen Preston (R) about the Bergdahl prisoner exchange at a House Armed Services Committee hearing on Capitol Hill in Washington June 11, 2014.  </P><P class="credit">Credit: Reuters/Jonathan Ernst</P></DIV></DIV></DIV></DIV><DIV class="columnLeft"><DIV class="relatedRail gridPanel grid2"><DIV id="relatedTopics" class="module"><DIV class="moduleBody"><UL><LI><A href="/politics">Politics \xbb</A></LI></UL></DIV></DIV></DIV></DIV><SPAN id="articleText"><SPAN class="focusParagraph"><P><SPAN class="articleLocation">WASHINGTON</SPAN> (Reuters) - Defense Secretary Chuck Hagel told a contentious congressional hearing on Wednesday the exchange of five Taliban leaders for war prisoner Bowe Bergdahl was an imperfect decision that eroded trust with Congress but he denied it involved negotiating with terrorists.</P></SPAN><P>Hagel told the House Armed Services Committee that President Barack Obama\'s approval of the prisoner exchange was the correct decision because it kept faith with the military\'s pledge not to leave troops behind. But he admitted &quot;trust has been broken&quot; by the failure to keep Congress adequately informed about the deal.</P><P>Lawmakers have criticized the administration for sending the five Taliban leaders held at Guantanamo prison to Qatar without giving them 30 days notice as required by law. They also have said the deal amounted to negotiating with terrorists.</P><P>&quot;Bergdahl was a detained combatant being held by an enemy force, and not a hostage,&quot; Hagel said.</P><P>Angry Republican lawmakers reacted skeptically to Hagel\'s explanation of the administration\'s actions, accusing him of not trusting Congress. One questioned the military\'s rationale for  holding Bergdahl at a U.S. military hospital in Germany since his release on May 31 from Afghanistan.</P><P>&quot;You\'re trying to tell me that he\'s being held in Landstuhl, Germany, because of his medical condition?&quot; Representative Jeff Miller asked.</P><P>&quot;I hope you\'re not implying anything other than that,&quot; Hagel replied, noting Bergdahl was receiving both physical and psychological treatment after five years as a prisoner of the Taliban. &quot;I don\'t like the implication of the question.&quot;</P><P>The initial euphoria over 28-year-old Bergdahl\'s release swiftly ebbed, with some of his former comrades accusing him of deserting his post in 2009 before his capture.</P><P>Hagel said he had been &quot;offended and disappointed&quot; by some of the treatment of Bergdahl\'s family. He said a comprehensive Army review would look at the legal issues surrounding Bergdahl\'s disappearance and capture.    &quot;His conduct will be judged on facts, not hearsay, posturing, charges or innuendo,&quot; Hagel said.</P><P>Hagel said the Obama administration felt a growing sense of urgency about freeing Bergdahl in the weeks leading up to the swap because of fears his health was deteriorating and warnings from Qatari intermediaries that &quot;time was not on our side.&quot;</P><P>&quot;We grew increasingly concerned that any delay, or any leaks, could derail the deal and further endanger Sergeant Bergdahl,&quot; Hagel said. &quot;We were told by Qataris that a leak would end the negotiations for Bergdahl\'s release.&quot;</P><P>Efforts to secure Bergdahl\'s freedom began to quicken in January after the administration received a &quot;proof of life&quot; video from the Taliban through the Qatari intermediaries.</P><P>&quot;It was disturbing,&quot; Hagel said. &quot;It showed a deterioration in his physical appearance and mental state.&quot;</P><P>Feeling a greater sense of urgency because of the video and a break-off in indirect talks, the administration negotiated a memorandum of understanding in early May with Qatar detailing the security measures that would be enforced if any Taliban detainees were transferred to their custody, he said.</P><P>After the memo was signed, U.S. officials received a warning from Qatari intermediaries that &quot;time was not on our side,&quot; Hagel said. They moved forward with indirect talks on the mechanism for the prisoner swap, reaching a deal on May 27.</P><P>&quot;We were told by the Qataris that a leak would end the negotiations for Bergdahl\'s release,&quot; Hagel said.</P><P>The U.S. defense chief said the swap was set in motion just four days later. He said U.S. forces did not know the general area of the handoff until 24 hours beforehand and did not have the precise location until one hour before the swap.</P><P> (Editing by Jason Szep and Grant McCool)</P></SPAN><DIV class="relatedTopicButtons"><DIV class="file_under">FILED UNDER: </DIV></DIV></DIV></DIV></DIV></DIV></DIV></BODY></HTML>';
var nestedHtml = [];
var extractedCounter = 0;
var compare = 0;
var extractionCnt = 0; //for appending the tokenization
var extractionCntReal = 0; //for appending the tokenization for REAL
var extractionCntRealNested = 0; //for appending the tokenization for REAL *for NESTED (can't believe I am adding a new one)
var entArray = ["Hello","world",",","welcome","to","the","multiverse","."]; //entire tokenized text
var extractedHtml;
// var test = ['Defense', 'chief', 'defends', 'Taliban', 'prisoner', 'swap', 'before', 'Congress', 'By', 'David', 'Alexander', 'Email', 'Print', '1', 'of', '3', '.', 'U', '.', 'S', '.', 'Defense', 'Secretary', 'Chuck', 'Hagel', '(', 'L', ')', 'testifies', 'with', 'Defense', 'Department', 'General', 'Counsel', 'Stephen', 'Preston', '(', 'R', ')', 'about', 'the', 'Bergdahl', 'prisoner', 'exchange', 'at', 'a', 'House', 'Armed', 'Services', 'Committee', 'hearing', 'on', 'Capitol', 'Hill', 'in', 'Washington', 'June', '11', ',', '2014', '.', 'Credit', ':', 'Reuters', '/', 'Jonathan', 'Ernst', 'Politics', '\xbb', 'WASHINGTON', '(', 'Reuters', ')', '-', 'Defense', 'Secretary', 'Chuck', 'Hagel', 'told', 'a', 'contentious', 'congressional', 'hearing', 'on', 'Wednesday', 'the', 'exchange', 'of', 'five', 'Taliban', 'leaders', 'for', 'war', 'prisoner', 'Bowe', 'Bergdahl', 'was', 'an', 'imperfect', 'decision', 'that', 'eroded', 'trust', 'with', 'Congress', 'but', 'he', 'denied', 'it', 'involved', 'negotiating', 'with', 'terrorists', '.', 'Hagel', 'told', 'the', 'House', 'Armed', 'Services', 'Committee', 'that', 'President', 'Barack', 'Obama', "'", 's', 'approval', 'of', 'the', 'prisoner', 'exchange', 'was', 'the', 'correct', 'decision', 'because', 'it', 'kept', 'faith', 'with', 'the', 'military', "'", 's', 'pledge', 'not', 'to', 'leave', 'troops', 'behind', '.', 'But', 'he', 'admitted', '"', 'trust', 'has', 'been', 'broken', '"', 'by', 'the', 'failure', 'to', 'keep', 'Congress', 'adequately', 'informed', 'about', 'the', 'deal', '.', 'Lawmakers', 'have', 'criticized', 'the', 'administration', 'for', 'sending', 'the', 'five', 'Taliban', 'leaders', 'held', 'at', 'Guantanamo', 'prison', 'to', 'Qatar', 'without', 'giving', 'them', '30', 'days', 'notice', 'as', 'required', 'by', 'law', '.', 'They', 'also', 'have', 'said', 'the', 'deal', 'amounted', 'to', 'negotiating', 'with', 'terrorists', '.', '"', 'Bergdahl', 'was', 'a', 'detained', 'combatant', 'being', 'held', 'by', 'an', 'enemy', 'force', ',', 'and', 'not', 'a', 'hostage', ',"', 'Hagel', 'said', '.', 'Angry', 'Republican', 'lawmakers', 'reacted', 'skeptically', 'to', 'Hagel', "'", 's', 'explanation', 'of', 'the', 'administration', "'", 's', 'actions', ',', 'accusing', 'him', 'of', 'not', 'trusting', 'Congress', '.', 'One', 'questioned', 'the', 'military', "'", 's', 'rationale', 'for', 'holding', 'Bergdahl', 'at', 'a', 'U', '.', 'S', '.', 'military', 'hospital', 'in', 'Germany', 'since', 'his', 'release', 'on', 'May', '31', 'from', 'Afghanistan', '.', '"', 'You', "'", 're', 'trying', 'to', 'tell', 'me', 'that', 'he', "'", 's', 'being', 'held', 'in', 'Landstuhl', ',', 'Germany', ',', 'because', 'of', 'his', 'medical', 'condition', '?"', 'Representative', 'Jeff', 'Miller', 'asked', '.', '"', 'I', 'hope', 'you', "'", 're', 'not', 'implying', 'anything', 'other', 'than', 'that', ',"', 'Hagel', 'replied', ',', 'noting', 'Bergdahl', 'was', 'receiving', 'both', 'physical', 'and', 'psychological', 'treatment', 'after', 'five', 'years', 'as', 'a', 'prisoner', 'of', 'the', 'Taliban', '.', '"', 'I', 'don', "'", 't', 'like', 'the', 'implication', 'of', 'the', 'question', '."', 'The', 'initial', 'euphoria', 'over', '28', '-', 'year', '-', 'old', 'Bergdahl', "'", 's', 'release', 'swiftly', 'ebbed', ',', 'with', 'some', 'of', 'his', 'former', 'comrades', 'accusing', 'him', 'of', 'deserting', 'his', 'post', 'in', '2009', 'before', 'his', 'capture', '.', 'Hagel', 'said', 'he', 'had', 'been', '"', 'offended', 'and', 'disappointed', '"', 'by', 'some', 'of', 'the', 'treatment', 'of', 'Bergdahl', "'", 's', 'family', '.', 'He', 'said', 'a', 'comprehensive', 'Army', 'review', 'would', 'look', 'at', 'the', 'legal', 'issues', 'surrounding', 'Bergdahl', "'", 's', 'disappearance', 'and', 'capture', '.', '"', 'His', 'conduct', 'will', 'be', 'judged', 'on', 'facts', ',', 'not', 'hearsay', ',', 'posturing', ',', 'charges', 'or', 'innuendo', ',"', 'Hagel', 'said', '.', 'Hagel', 'said', 'the', 'Obama', 'administration', 'felt', 'a', 'growing', 'sense', 'of', 'urgency', 'about', 'freeing', 'Bergdahl', 'in', 'the', 'weeks', 'leading', 'up', 'to', 'the', 'swap', 'because', 'of', 'fears', 'his', 'health', 'was', 'deteriorating', 'and', 'warnings', 'from', 'Qatari', 'intermediaries', 'that', '"', 'time', 'was', 'not', 'on', 'our', 'side', '."', '"', 'We', 'grew', 'increasingly', 'concerned', 'that', 'any', 'delay', ',', 'or', 'any', 'leaks', ',', 'could', 'derail', 'the', 'deal', 'and', 'further', 'endanger', 'Sergeant', 'Bergdahl', ',"', 'Hagel', 'said', '.', '"', 'We', 'were', 'told', 'by', 'Qataris', 'that', 'a', 'leak', 'would', 'end', 'the', 'negotiations', 'for', 'Bergdahl', "'", 's', 'release', '."', 'Efforts', 'to', 'secure', 'Bergdahl', "'", 's', 'freedom', 'began', 'to', 'quicken', 'in', 'January', 'after', 'the', 'administration', 'received', 'a', '"', 'proof', 'of', 'life', '"', 'video', 'from', 'the', 'Taliban', 'through', 'the', 'Qatari', 'intermediaries', '.', '"', 'It', 'was', 'disturbing', ',"', 'Hagel', 'said', '.', '"', 'It', 'showed', 'a', 'deterioration', 'in', 'his', 'physical', 'appearance', 'and', 'mental', 'state', '."', 'Feeling', 'a', 'greater', 'sense', 'of', 'urgency', 'because', 'of', 'the', 'video', 'and', 'a', 'break', '-', 'off', 'in', 'indirect', 'talks', ',', 'the', 'administration', 'negotiated', 'a', 'memorandum', 'of', 'understanding', 'in', 'early', 'May', 'with', 'Qatar', 'detailing', 'the', 'security', 'measures', 'that', 'would', 'be', 'enforced', 'if', 'any', 'Taliban', 'detainees', 'were', 'transferred', 'to', 'their', 'custody', ',', 'he', 'said', '.', 'After', 'the', 'memo', 'was', 'signed', ',', 'U', '.', 'S', '.', 'officials', 'received', 'a', 'warning', 'from', 'Qatari', 'intermediaries', 'that', '"', 'time', 'was', 'not', 'on', 'our', 'side', ',"', 'Hagel', 'said', '.', 'They', 'moved', 'forward', 'with', 'indirect', 'talks', 'on', 'the', 'mechanism', 'for', 'the', 'prisoner', 'swap', ',', 'reaching', 'a', 'deal', 'on', 'May', '27', '.', '"', 'We', 'were', 'told', 'by', 'the', 'Qataris', 'that', 'a', 'leak', 'would', 'end', 'the', 'negotiations', 'for', 'Bergdahl', "'", 's', 'release', ',"', 'Hagel', 'said', '.', 'The', 'U', '.', 'S', '.', 'defense', 'chief', 'said', 'the', 'swap', 'was', 'set', 'in', 'motion', 'just', 'four', 'days', 'later', '.', 'He', 'said', 'U', '.', 'S', '.', 'forces', 'did', 'not', 'know', 'the', 'general', 'area', 'of', 'the', 'handoff', 'until', '24', 'hours', 'beforehand', 'and', 'did', 'not', 'have', 'the', 'precise', 'location', 'until', 'one', 'hour', 'before', 'the', 'swap', '.', '(', 'Editing', 'by', 'Jason', 'Szep', 'and', 'Grant', 'McCool', ')', 'FILED', 'UNDER', ':'];
var spanid = 0;
var testclass = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
var testtext = ['Defense', 'chief', 'defends', 'Taliban', 'prisoner', 'swap', 'before', 'Congress', 'By', 'David', 'Alexander', 'Email', 'Print', '1', 'of', '3', '.', 'U', '.', 'S', '.', 'Defense', 'Secretary', 'Chuck', 'Hagel', '(', 'L', ')', 'testifies', 'with', 'Defense', 'Department', 'General', 'Counsel', 'Stephen', 'Preston', '(', 'R', ')', 'about', 'the', 'Bergdahl', 'prisoner', 'exchange', 'at', 'a', 'House', 'Armed', 'Services', 'Committee', 'hearing', 'on', 'Capitol', 'Hill', 'in', 'Washington', 'June', '11', ',', '2014', '.', 'Credit', ':', 'Reuters', '/', 'Jonathan', 'Ernst', 'Politics', '»', 'WASHINGTON', '(', 'Reuters', ')', '-', 'Defense', 'Secretary', 'Chuck', 'Hagel', 'told', 'a', 'contentious', 'congressional', 'hearing', 'on', 'Wednesday', 'the', 'exchange', 'of', 'five', 'Taliban', 'leaders', 'for', 'war', 'prisoner', 'Bowe', 'Bergdahl', 'was', 'an', 'imperfect', 'decision', 'that', 'eroded', 'trust', 'with', 'Congress', 'but', 'he', 'denied', 'it', 'involved', 'negotiating', 'with', 'terrorists', '.', 'Hagel', 'told', 'the', 'House', 'Armed', 'Services', 'Committee', 'that', 'President', 'Barack', 'Obama', "'", 's', 'approval', 'of', 'the', 'prisoner', 'exchange', 'was', 'the', 'correct', 'decision', 'because', 'it', 'kept', 'faith', 'with', 'the', 'military', "'", 's', 'pledge', 'not', 'to', 'leave', 'troops', 'behind', '.', 'But', 'he', 'admitted', '"', 'trust', 'has', 'been', 'broken', '"', 'by', 'the', 'failure', 'to', 'keep', 'Congress', 'adequately', 'informed', 'about', 'the', 'deal', '.', 'Lawmakers', 'have', 'criticized', 'the', 'administration', 'for', 'sending', 'the', 'five', 'Taliban', 'leaders', 'held', 'at', 'Guantanamo', 'prison', 'to', 'Qatar', 'without', 'giving', 'them', '30', 'days', 'notice', 'as', 'required', 'by', 'law', '.', 'They', 'also', 'have', 'said', 'the', 'deal', 'amounted', 'to', 'negotiating', 'with', 'terrorists', '.', '"', 'Bergdahl', 'was', 'a', 'detained', 'combatant', 'being', 'held', 'by', 'an', 'enemy', 'force', ',', 'and', 'not', 'a', 'hostage', ',"', 'Hagel', 'said', '.', 'Angry', 'Republican', 'lawmakers', 'reacted', 'skeptically', 'to', 'Hagel', "'", 's', 'explanation', 'of', 'the', 'administration', "'", 's', 'actions', ',', 'accusing', 'him', 'of', 'not', 'trusting', 'Congress', '.', 'One', 'questioned', 'the', 'military', "'", 's', 'rationale', 'for', 'holding', 'Bergdahl', 'at', 'a', 'U', '.', 'S', '.', 'military', 'hospital', 'in', 'Germany', 'since', 'his', 'release', 'on', 'May', '31', 'from', 'Afghanistan', '.', '"', 'You', "'", 're', 'trying', 'to', 'tell', 'me', 'that', 'he', "'", 's', 'being', 'held', 'in', 'Landstuhl', ',', 'Germany', ',', 'because', 'of', 'his', 'medical', 'condition', '?"', 'Representative', 'Jeff', 'Miller', 'asked', '.', '"', 'I', 'hope', 'you', "'", 're', 'not', 'implying', 'anything', 'other', 'than', 'that', ',"', 'Hagel', 'replied', ',', 'noting', 'Bergdahl', 'was', 'receiving', 'both', 'physical', 'and', 'psychological', 'treatment', 'after', 'five', 'years', 'as', 'a', 'prisoner', 'of', 'the', 'Taliban', '.', '"', 'I', 'don', "'", 't', 'like', 'the', 'implication', 'of', 'the', 'question', '."', 'The', 'initial', 'euphoria', 'over', '28', '-', 'year', '-', 'old', 'Bergdahl', "'", 's', 'release', 'swiftly', 'ebbed', ',', 'with', 'some', 'of', 'his', 'former', 'comrades', 'accusing', 'him', 'of', 'deserting', 'his', 'post', 'in', '2009', 'before', 'his', 'capture', '.', 'Hagel', 'said', 'he', 'had', 'been', '"', 'offended', 'and', 'disappointed', '"', 'by', 'some', 'of', 'the', 'treatment', 'of', 'Bergdahl', "'", 's', 'family', '.', 'He', 'said', 'a', 'comprehensive', 'Army', 'review', 'would', 'look', 'at', 'the', 'legal', 'issues', 'surrounding', 'Bergdahl', "'", 's', 'disappearance', 'and', 'capture', '.', '"', 'His', 'conduct', 'will', 'be', 'judged', 'on', 'facts', ',', 'not', 'hearsay', ',', 'posturing', ',', 'charges', 'or', 'innuendo', ',"', 'Hagel', 'said', '.', 'Hagel', 'said', 'the', 'Obama', 'administration', 'felt', 'a', 'growing', 'sense', 'of', 'urgency', 'about', 'freeing', 'Bergdahl', 'in', 'the', 'weeks', 'leading', 'up', 'to', 'the', 'swap', 'because', 'of', 'fears', 'his', 'health', 'was', 'deteriorating', 'and', 'warnings', 'from', 'Qatari', 'intermediaries', 'that', '"', 'time', 'was', 'not', 'on', 'our', 'side', '."', '"', 'We', 'grew', 'increasingly', 'concerned', 'that', 'any', 'delay', ',', 'or', 'any', 'leaks', ',', 'could', 'derail', 'the', 'deal', 'and', 'further', 'endanger', 'Sergeant', 'Bergdahl', ',"', 'Hagel', 'said', '.', '"', 'We', 'were', 'told', 'by', 'Qataris', 'that', 'a', 'leak', 'would', 'end', 'the', 'negotiations', 'for', 'Bergdahl', "'", 's', 'release', '."', 'Efforts', 'to', 'secure', 'Bergdahl', "'", 's', 'freedom', 'began', 'to', 'quicken', 'in', 'January', 'after', 'the', 'administration', 'received', 'a', '"', 'proof', 'of', 'life', '"', 'video', 'from', 'the', 'Taliban', 'through', 'the', 'Qatari', 'intermediaries', '.', '"', 'It', 'was', 'disturbing', ',"', 'Hagel', 'said', '.', '"', 'It', 'showed', 'a', 'deterioration', 'in', 'his', 'physical', 'appearance', 'and', 'mental', 'state', '."', 'Feeling', 'a', 'greater', 'sense', 'of', 'urgency', 'because', 'of', 'the', 'video', 'and', 'a', 'break', '-', 'off', 'in', 'indirect', 'talks', ',', 'the', 'administration', 'negotiated', 'a', 'memorandum', 'of', 'understanding', 'in', 'early', 'May', 'with', 'Qatar', 'detailing', 'the', 'security', 'measures', 'that', 'would', 'be', 'enforced', 'if', 'any', 'Taliban', 'detainees', 'were', 'transferred', 'to', 'their', 'custody', ',', 'he', 'said', '.', 'After', 'the', 'memo', 'was', 'signed', ',', 'U', '.', 'S', '.', 'officials', 'received', 'a', 'warning', 'from', 'Qatari', 'intermediaries', 'that', '"', 'time', 'was', 'not', 'on', 'our', 'side', ',"', 'Hagel', 'said', '.', 'They', 'moved', 'forward', 'with', 'indirect', 'talks', 'on', 'the', 'mechanism', 'for', 'the', 'prisoner', 'swap', ',', 'reaching', 'a', 'deal', 'on', 'May', '27', '.', '"', 'We', 'were', 'told', 'by', 'the', 'Qataris', 'that', 'a', 'leak', 'would', 'end', 'the', 'negotiations', 'for', 'Bergdahl', "'", 's', 'release', ',"', 'Hagel', 'said', '.', 'The', 'U', '.', 'S', '.', 'defense', 'chief', 'said', 'the', 'swap', 'was', 'set', 'in', 'motion', 'just', 'four', 'days', 'later', '.', 'He', 'said', 'U', '.', 'S', '.', 'forces', 'did', 'not', 'know', 'the', 'general', 'area', 'of', 'the', 'handoff', 'until', '24', 'hours', 'beforehand', 'and', 'did', 'not', 'have', 'the', 'precise', 'location', 'until', 'one', 'hour', 'before', 'the', 'swap', '.', '(', 'Editing', 'by', 'Jason', 'Szep', 'and', 'Grant', 'McCool', ')', 'FILED', 'UNDER', ':'];


//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//~~~~~~~~~~~~~~~~~~~~~~~(\_______/)~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//~~~~~~~~~~~~~~~~~~~~~~~~(｡◕‿‿◕｡)~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//~~~~~~~~~~~~~~~~~~~~~~~z(＿つ＿_つ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//start of the code for corrections
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


// Returns the ids of the spans between firstEl and lastEl

function correction(correct, ids) {
    $.ajax({
            // dataType: "json",
            type: "POST",
// link is sent to this url for corrections
            url: "http://eltanin.cis.cornell.edu/reflection/corrections",
            data: {
                url: document.URL,
                correction: correct,
                ids: ids,
                activationKey: activationKey
            },

        })
    .done(function() {
    });
}


function getSpanIds(firstEl, lastEl) {
    var firstElement = $(firstEl);
    var lastElement = $(lastEl);
    var collection = new Array();
    if ((!firstElement.hasClass("space")) || (firstEl == lastEl)) {
        collection.push(firstElement.attr('id'));
    }
    if (firstEl != lastEl) {
        $(firstEl).nextAll().each(function () {
            var siblingID = $(this).attr('id');
            if (siblingID != $(lastElement).attr('id')) {
                collection.push($(this).attr('id'));
            } else {
                collection.push(lastElement.attr('id'));
                return false;
            }
        });
    }
    return collection;
}

//Un-Highlights the selected words
function unhighlightAnnotate(ids) {
    var idx = 0;
    var end = ids.length;
    highlight_index++;
    var selectNow = '';

    //strip spaces
    if ($('#' + ids[0]).hasClass("space")) {
        idx = 1;
    }
    if ($('#' + ids[end - 1]).hasClass("space")) {
        end = ids.length - 1;
    }

    //highlight
    for (i = idx; i < end; i++) {
        if ($("#" + ids[i]).hasClass("highlight")) {
            $("#" + ids[i]).removeClass("highlight")
        }
        selectNow = selectNow + $("#" + ids[i]).text() + " ";
    }
    return selectNow;
}


//Highlights the selected words
function highlightAnnotate(ids) {
    var idx = 0;
    var end = ids.length;
    highlight_index++;
    var selectNow = '';

    //strip spaces
    if ($('#' + ids[0]).hasClass("space")) {
        idx = 1;
    }
    if ($('#' + ids[end - 1]).hasClass("space")) {
        end = ids.length - 1;
    }

    //highlight
    for (i = idx; i < end; i++) {
        $("#" + ids[i]).addClass("highlight");
        selectNow = selectNow + $("#" + ids[i]).text() + " ";
    }

    return selectNow;
}



//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~(\_______/)~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~(｡◕‿‿◕｡)~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~z(＿つ＿_つ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//end of the code for corrections
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
//~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

function walkExtract(node) {
        // Function from http://is.gd/mwZp7Estr
        // through cloud-to-butt
        var child, next;
        switch (node.nodeType) {
        case 1: // Element
        case 9: // Document
        case 11: // Document fragment
            child = node.firstChild;
            while (child) {
                next = child.nextSibling;
                walkExtract(child);
                child = next;
            }
            break;
        case 3: // Text node
            var extractedNode =[];
            var tempStrW = node.textContent;
            var strW = tempStrW.replace(/\s/g, '');

            // alert(strW);
            while(strW.length>0){
                // console.log(entArray[extractionCnt]);
                var entArrayNoSpace = entArray[extractionCnt].toLowerCase().replace(/\s/g, '');
                if((strW.toLowerCase().indexOf("hide")==0)&&(entArray[extractionCnt+1].toLowerCase().replace(/\s/g, '').indexOf("caption")==0)){
                    testtext.splice(extractionCnt,1);
                    testclass.splice(extractionCnt,1);
                }

                else if(strW.toLowerCase().indexOf(entArrayNoSpace)==0){
                var strwNoSpace = strW.slice(0,entArrayNoSpace.length);
                    extractedNode.push(strwNoSpace);
                    // alert(strW);
                    strW = strW.slice(entArrayNoSpace.length);
                    extractionCnt=extractionCnt+1;
                }
                else if(entArray[extractionCnt].indexOf("caption")== 0 && entArray[extractionCnt].length > 11){
                    entArray[extractionCnt] = entArray[extractionCnt].slice(7);
                }

                else if((extractionCnt!=0)&&(entArray[extractionCnt-1][entArray[extractionCnt-1].length-1]==".") && (entArray[extractionCnt] == ".")){
                    testtext.splice(extractionCnt,1);
                    testclass.splice(extractionCnt,1);
                }

                else {
                    strW = strW.slice(1);
                    return false;
                }
            }
            
            nestedHtml[extractedCounter] = extractedNode;
            extractedCounter = extractedCounter + 1;
            break;
        }
    }


function activationFunction() {

    activationKey = activation;
    if (activation != undefined && activation != "") {
        console.log(masterWhiteList.length);
        for (mwlCnt = 0; mwlCnt < masterWhiteList.length; mwlCnt++) {
            // console.log(masterWhiteList[mwlCnt]);
            sourceUrl = sourceUrl.replace('www.', '');
            // console.log(sourceUrl);
            var masterUrl = masterWhiteList[mwlCnt].replace('http://', '').replace('https://', '').replace('http://www.', '').replace('https://www.', '').replace('www.', '').split(/[/?#]/)[0];
            // console.log(masterUrl);
            //stop NYTimes
            if(sourceUrl == "nytimes.com"){
                console.log("NYTimes error: Known issue")
                return false;
            }
            if (sourceUrl == masterUrl) {
                break;
            }
            if (mwlCnt + 1 == masterWhiteList.length) {
                if (sourceUrl != masterUrl) {
                    return false;
                }

            }
        }
        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~INITIAL AJAX CALL~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
chrome.runtime.sendMessage({starting: "go"});
$.ajax({
        dataType: "json",
        type: "POST",
// url for initial ajax, checking for activation
        url: "http://eltanin.cis.cornell.edu/reflection",
        data: {
            url: document.URL,
            activationKey: activationKey
        },
        crossDomain: true,
    success: function (result) {
            chrome.runtime.sendMessage({starting: "done"});
        
        var obj = result;
        testtext = obj.wordlist;
        entArray = obj.wordlist;
        console.log(obj.wordlist);
        console.log(obj.html);
        extractedHtmlText = obj.html; //html
        testclass = obj.predictions;
        console.log(obj.predictions);

        //-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
        extractedHtmlText = extractedHtmlText.replace(/\xa0/g, '');
        extractedHtml = $.parseHTML(extractedHtmlText);


        for (initCheck = 0; initCheck < extractedHtml.length; initCheck++) {
            if ((extractedHtml[initCheck].toString() == '[object Text]') || (extractedHtml[initCheck].toString() == '[object HTMLStyleElement]')) {
                //         alert(extractedHtml[initCheck]);
                continue;
            } else {
                walkExtract(extractedHtml[initCheck]);

            }
            console.log(nestedHtml);
        }
        for (var indexer = nestedHtml.length - 1; indexer--;) {
            // remove null array elements from nestedHtml
            if (nestedHtml[indexer] == null) nestedHtml.splice(indexer, 1);
        }
        walk(document.body);
        
        //-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/-/
        },
        error: function () {
            // alert("Failed to Access Server, Please Contact Us.");
            chrome.runtime.sendMessage({starting: "stop"});
        }
    });
// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~END INITIAL AJAX CALL~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



        chrome.extension.onMessage.addListener(function (message, sender, callback) {
            if (message.functiontoInvoke == "annotate") {
                $('#annotate').trigger("click");
            }
            if (message.functiontoInvoke == "denotate") {
                $('#denotate').trigger("click");
            }
        });

        // Highlighting function
        $(document).ready(function () {
            $('#annotate').click(function (event) {
                if (window.getSelection) {
                    userSelection = window.getSelection();
                    selectionString = userSelection.toString();
                    rangeObject = userSelection.getRangeAt(0);
                    var start = rangeObject.startContainer;
                    var end = rangeObject.endContainer;
                    var ids = getSpanIds(start.parentNode, end.parentNode);
                    // alert(ids.length);
                    // console.log(ids);
                    words = highlightAnnotate(ids);
                    var idsTemp = [];
                    for (idscnt=0; idscnt < ids.length; idscnt++){
                        if(ids[idscnt]!=undefined){
                            idsTemp.push(ids[idscnt]);
                        }
                    }
                    correction(1, idsTemp);
                }
            });

            $(document).ready(function () {
                $('#denotate').click(function (event) {
                    if (window.getSelection) {
                        userSelection = window.getSelection();
                        selectionString = userSelection.toString();
                        rangeObject = userSelection.getRangeAt(0);
                        var start = rangeObject.startContainer;
                        var end = rangeObject.endContainer;
                        var ids = getSpanIds(start.parentNode, end.parentNode);
                        // console.log(ids);
                        words = unhighlightAnnotate(ids);
                        var idsTemp = [];
                        for (idscnt=0; idscnt < ids.length; idscnt++){
                            if(ids[idscnt]!=undefined){
                                idsTemp.push(ids[idscnt]);
                                // alert(idsTemp);
                            }
                        }
                        correction(0, idsTemp);
                    }
                })
            });
        });
    }
}


function walk(node) {
    // Function from http://is.gd/mwZp7Estr
    // through cloud-to-butt
    var child, next;
    switch (node.nodeType) {
    case 1: // Element
    case 9: // Document
    case 11: // Document fragment
        child = node.firstChild;
        while (child) {
            next = child.nextSibling;
            walk(child);
            child = next;
        }
        break;
    case 3: // Text node
        replaceElement(node);
        break;
    }
}


function highlight(str) {
    var e = document.createElement("span");
    e.setAttribute("class", "highlight");
    e.setAttribute("style", "display:inline;");
    e.setAttribute("id", spanid.toString());
    spanid = spanid + 1;
    e.appendChild(document.createTextNode(str));
    return e;
}


function spanner(str) {
    var e = document.createElement("span");
    var countid = spanid.toString()
    e.setAttribute("id", countid);
    e.setAttribute("class", "spans");
    e.setAttribute("style", "display:inline;");
    // e.setAttribute("onMouseOver", "expand(" + countid + ")");
    // e.setAttribute("onmouseout", "expand(" + countid + ")");
    spanid = spanid + 1;
    e.appendChild(document.createTextNode(str));
    return e;
}


function replaceElement(node) {
    elem = node.parentNode;
    for (var q = elem.childNodes.length; q--;) {
        var childNode = elem.childNodes[q];
        if (childNode.nodeType == 3) { // 3 => a Text Node
            var strSrc = childNode.nodeValue; // for Text Nodes, the nodeValue property contains the text
            var strTemp = strSrc;
            var str = strTemp;
            

            var trimmed =[];  
            // var trimmed = str.match(/\w+|[^\w\s]+/g);

            str = str.replace(/\s/g, '');
            var strEarly = str;    
            var trimmedAlt = [];
            var extractionCntRealAlt = extractionCntReal;
            
            while(str.length>0){
            var entArrayNoSpaceReal = nestedHtml[extractionCntRealNested][extractionCntRealAlt].toLowerCase().replace(/\s/g, '');
            if((nestedHtml[extractionCntRealNested].length == 2) && (extractionCntRealAlt==0)) {
                var extractionCntRealAltTemp = extractionCntRealAlt +1;
                var entArrayNoSpaceReal2 = nestedHtml[extractionCntRealNested][extractionCntRealAltTemp].toLowerCase().replace(/\s/g, '');
                if((entArrayNoSpaceReal == "follow") && (entArrayNoSpaceReal2.indexOf("@") == 0)
                    ) {
                    testclass = testclass.slice(2);
                    testtext = testtext.slice(2);
                    extractionCntRealAlt = 0;
                    extractionCntReal = extractionCntRealAlt;
                    extractionCntRealNested = extractionCntRealNested + 1;
                    entArrayNoSpaceReal = nestedHtml[extractionCntRealNested][extractionCntRealAlt].toLowerCase().replace(/\s/g, '');
                    compare = compare + 1;
                }
            }
                if (((entArrayNoSpaceReal === "tweet") && (nestedHtml[extractionCntRealNested].length == 1))||
                    ((entArrayNoSpaceReal === "post") && (nestedHtml[extractionCntRealNested].length == 1))||
                    ((entArrayNoSpaceReal === ".") && (nestedHtml[extractionCntRealNested].length == 1))||
                    ((entArrayNoSpaceReal === "email") && (nestedHtml[extractionCntRealNested].length == 1))||
                    ((entArrayNoSpaceReal === "facebook") && (nestedHtml[extractionCntRealNested].length == 1))||
                    ((entArrayNoSpaceReal === "e-mail") && (nestedHtml[extractionCntRealNested].length == 1))||
                    ((entArrayNoSpaceReal === "…") && (nestedHtml[extractionCntRealNested].length == 1))||
                    ((entArrayNoSpaceReal === "(") && (nestedHtml[extractionCntRealNested].length == 1))||
                    ((entArrayNoSpaceReal === "ccomments") && (nestedHtml[extractionCntRealNested].length == 1))||
                    ((entArrayNoSpaceReal === "0") && (nestedHtml[extractionCntRealNested].length == 1))||
                    ((entArrayNoSpaceReal === "twitter") && (nestedHtml[extractionCntRealNested].length == 1))||
                    ((entArrayNoSpaceReal === "livefyre") && (nestedHtml[extractionCntRealNested].length == 1))||
                    ((entArrayNoSpaceReal === ")") && (nestedHtml[extractionCntRealNested].length == 1))

                    ) {
                    // alert(nestedHtml[extractionCntRealNested].length);
                    // extractionCntRealAlt = 0;
                    // extractionCntReal = extractionCntRealAlt;
                    // trimmed.push(entArrayNoSpaceReal);
                    // extractionCntRealNested = extractionCntRealNested + 1;

                    testclass = testclass.slice(1);
                    testtext = testtext.slice(1);
                    extractionCntRealAlt = 0;
                    extractionCntReal = extractionCntRealAlt;
                    extractionCntRealNested = extractionCntRealNested + 1;
                    entArrayNoSpaceReal = nestedHtml[extractionCntRealNested][extractionCntRealAlt].toLowerCase().replace(/\s/g, '');
                    compare = compare + 1;
                }

                if(strEarly.toLowerCase().indexOf(entArrayNoSpaceReal)==0){
                    // console.log(entArrayNoSpaceReal + " dis at end do");
                    var lastCheck = strEarly.slice(0,entArrayNoSpaceReal.length);
                    trimmedAlt.push(strEarly.slice(0,entArrayNoSpaceReal.length));
                    strEarly = strEarly.slice(entArrayNoSpaceReal.length);
                    extractionCntRealAlt = extractionCntRealAlt + 1;

                }
                else {

                    break;
                }
                if(!(strEarly.length>0) && (nestedHtml[extractionCntRealNested][nestedHtml[extractionCntRealNested].length-1]==lastCheck)){
                    // console.log("gET HERE?");
                    extractionCntRealAlt = 0;
                    extractionCntReal = extractionCntRealAlt;
                    for(extraCnt=0; extraCnt < trimmedAlt.length; extraCnt++){
                        trimmed.push(trimmedAlt[extraCnt]);
                        
                        str = str.slice(trimmedAlt[extraCnt].length);
                        // console.log(str + " str");
                    }
                    extractionCntRealNested = extractionCntRealNested + 1;

                }
            }

            if (trimmed.length > 0) {
                for (comp = 0; comp < nestedHtml[compare].length; comp++) {
                    if (nestedHtml[compare].length - 1 == comp) {
                        var fragment = document.createElement("span");
                        fragment.setAttribute("class", "parent");
                        fragment.setAttribute("style", "display:inline;");
                        for (i = 0; i < trimmed.length; i++) {
                            if (trimmed[i].toLowerCase() != testtext[i]) {
                                delete fragment;
                                break;
                            } else {
                                
                                var strSearch = trimmed[i];
                                var pos = strSrc.toLowerCase().indexOf(strSearch.toLowerCase());
                                strSearch1 = strSrc.substring(pos, pos + strSearch.length);
                                if (testclass[i] == 1) {
                                    if (pos > 0) {
                                        //                                         fragment.appendChild(document.createTextNode(strSrc.substr(0, pos)));
                                        var whiteSpan = document.createElement("span");
                                        whiteSpan.setAttribute("class", "spans");
                                        whiteSpan.setAttribute("style", "display:inline;");

                                        whiteSpan.appendChild(document.createTextNode(strSrc.substr(0, pos)));
                                        fragment.appendChild(whiteSpan);
                                    }
                                    if (pos >= 0) {
                                        fragment.appendChild(highlight(strSearch1)); // calls function to add span tag
                                    }
                                } else {

                                    if (pos > 0) {
                                        //                                         fragment.appendChild(document.createTextNode(strSrc.substr(0, pos)));
                                        var whiteSpan = document.createElement("span");
                                        whiteSpan.setAttribute("class", "spans");
                                        whiteSpan.setAttribute("style", "display:inline;");
                                        whiteSpan.appendChild(document.createTextNode(strSrc.substr(0, pos)));
                                        fragment.appendChild(whiteSpan);
                                    }
                                    if (pos >= 0) {
                                        fragment.appendChild(spanner(strSearch1));
                                    }
                                }

                                //check for white space after text and append if found
                                if (strTemp.substring(strTemp.length - 1, strTemp.length) == ' ') { // check white space from end
                                    fragment.appendChild(document.createTextNode(' '));
                                }
                                strSrc = strSrc.substr(pos + strSearch1.length);
                            }
                       
                            if (i + 1 == trimmed.length) {
                                elem.replaceChild(fragment, childNode);
                                testclass = testclass.slice(trimmed.length);
                                testtext = testtext.slice(trimmed.length);
                                compare = compare + 1;
                            }
                        } //end of for loop
                    } //end else if (comparison)
                    if (nestedHtml[compare][comp] != trimmed[comp]) {
                        break;
                    }
                } //end for loop (comparison)
            }
        }
    }
}