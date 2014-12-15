// var matches = chrome.runtime.getManifest().content_scripts[0].matches;
// var pattern = new RegExp('^https?:\\/\\/(\\w+\\.)?(' +
//     matches.map(function(pattern) {
//       return RegExp.escape(pattern.substring(6, pattern.length - 2));
//     }).join('|') + ')\\/', 'i');

// chrome.webRequest.onBeforeSendHeaders.addListener(function(details) {
//   return {
//     cancel: details.requestHeaders.some(function(header) {
//       if (header.name == 'Referer' && pattern.test(header.value))
//         return true;
//     })
//   };
// }, {
//   urls: ['<all_urls>'],
//   types: ['script']
// }, ['blocking', 'requestHeaders']);


// var contentSettings = chrome.contentSettings;

// contentSettings.javascript.clear({}, function() {

// contentSettings.javascript.set({
//   primaryPattern: '*://*.reuters.com/*',
//   setting: 'block'
// });

// });


// chrome.webRequest.onBeforeRequest.addListener(
//         function(details) { return {cancel: true}; },
//         {urls: ["*://www.reuters.com/*"],
//         types: ['script']},
//         ["blocking", "requestHeaders"]);
      

// chrome.webRequest.onBeforeRequest.addListener(
//         function(details) {
//           return {cancel: details.url.indexOf("://www.reuters.com/") != -1};
//         },
//         {urls: ["<all_urls>"],
//         types: ['script']
//     },
//         ["blocking", 'requestHeaders']);
      


function annotate(info, tab) {
    chrome.tabs.query({
        "active": true,
        "currentWindow": true
    }, function (tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {
            "functiontoInvoke": "annotate"
        });
    });
}

function denotate(info, tab) {
    chrome.tabs.query({
        "active": true,
        "currentWindow": true
    }, function (tabs) {
        chrome.tabs.sendMessage(tabs[0].id, {
            "functiontoInvoke": "denotate"
        });
    });
}

var FrameCheck = chrome.contextMenus.create({"title": "FrameCheck", "contexts":["selection"]});
var highlighter = chrome.contextMenus.create(
  {"title": "Framing", "contexts":["selection"], "parentId": FrameCheck, "onclick": annotate});
var unhighlighter = chrome.contextMenus.create(
  {"title": "Unframed", "contexts":["selection"], "parentId": FrameCheck, "onclick": denotate});

// 


chrome.runtime.onMessage.addListener(
  function(request, sender, sendResponse) {
    if (request.starting == "go"){
        chrome.browserAction.setIcon({path:"loading.png"});
    }
    else if (request.starting == "stop"){
        chrome.browserAction.setIcon({path:"stop.png"});
    }
    else if (request.starting == "done"){
        chrome.browserAction.setIcon({path:"icon.png"});
    }
  });


