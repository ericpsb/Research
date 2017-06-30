window.fbAsyncInit = function() {
    FB.init({
    appId: '1582658458614337', // App ID
    status: true, // check login status
    cookie: true, // enable cookies to allow the
    // server to access the session
    xfbml: true, // parse page for xfbml or html5
    // social plugins like login button below
    version: 'v2.9', // Specify an API version
    });

    // Put additional init code here
};

(function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {
    return;
    }
    js = d.createElement(s);
    js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));


function getParamByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
    results = regex.exec(window.location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}
document.getElementById("return").onclick = function() {
    domain = "https://das-lab.org/";
    window.top.location.href = domain + "truefriend/initViz.php?resp=" + getParamByName('resp') + "&user=" + getParamByName('user');
};

var ac = getParamByName("resp");
var uid = getParamByName("user");

var sharefun = function(t) {
    FB.ui({
    method: 'share_open_graph',
    action_type: 'pages.saves',
    action_properties: JSON.stringify({
        object: 'https://das-lab.org/truefriend/',
        tags: t,
        access_token: ac
    })
    }, function(response) {});

};
