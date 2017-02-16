<?php
//Defining the name of the file
//$file = 'uids.txt';

//Need to capture resp variable from the HTTP Get variable
//$uid = $_GET['uid'];

//Let save this access token to the server for the future
//file_put_contents($file, $uid.PHP_EOL, FILE_APPEND);

?>
<!DOCTYPE html>
<html>
<head>
<title>True Friend Login</title>
 <meta charset="utf-8">
    <title>True Friend</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">

    <!-- Le styles -->
    <link href="../bootstrap.css" rel="stylesheet">
    <style type="text/css">
      body {
        padding-top: 60px;
        padding-bottom: 40px;
      }
    </style>
<link rel="stylesheet" type ="text/css" href="Woo10/css/animate.css">
<link rel="stylesheet" type ="text/css" href="Woo10/css/default.css">
<link rel="stylesheet" type ="text/css" href="Woo10/css/font-awesome/css/font-awesome.css">
<link rel="stylesheet" type ="text/css" href="Woo10/css/font-awesome/css/font-awesome.min.css">
<link rel="stylesheet" type ="text/css" href="Woo10/css/fontello/css/animation.css">
<link rel="stylesheet" type ="text/css" href="Woo10/css/fontello/css/fontello-codes.css">
<link rel="stylesheet" type ="text/css"  href="Woo10/css/fontello/css/fontello-embedded.css">
<link rel="stylesheet" type ="text/css"  href="Woo10/css/fontello/css/fontello-ie7-codes.css">
<link rel="stylesheet" type ="text/css"  href="Woo10/css/fontello/css/fontello-ie7.css">

    <link rel="stylesheet" type ="text/css"  href="Woo10/css/fontello/css/fontello.css">
<link rel="stylesheet" type ="text/css" href="Woo10/css/fonts.css">
<link rel="stylesheet" type ="text/css"  href="Woo10/css/layout.css">
<link rel="stylesheet" type ="text/css"  href="Woo10/css/media-queries.css">
<link rel="stylesheet" type ="text/css" href="Woo10/css/prettyPhoto.css">
    <!-- HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="../assets/js/html5shiv.js"></script>
    <![endif]-->

    <!-- Fav and touch icons -->
    <link rel="apple-touch-icon-precomposed" sizes="144x144" href="../assets/ico/apple-touch-icon-144-precomposed.png">
    <link rel="apple-touch-icon-precomposed" sizes="114x114" href="../assets/ico/apple-touch-icon-114-precomposed.png">
      <link rel="apple-touch-icon-precomposed" sizes="72x72" href="../assets/ico/apple-touch-icon-72-precomposed.png">
                    <link rel="apple-touch-icon-precomposed" href="../assets/ico/apple-touch-icon-57-precomposed.png">
                                   <link rel="shortcut icon" href="../assets/ico/favicon.png">
</head>
<body>
<script language="JavaScript">
  //Defining GET variable function
  function getQueryVariable(variable) { 
	var query = window.location.search.substring(1); 
	var vars = query.split("&"); 
	for (var i = 0; i < vars.length; i++) { 
		var pair = vars[i].split("="); 
		if (pair[0] == variable) { 
		return unescape(pair[1]); 
			} 
		}	 
	return false; 
	}  
  // This is called with the results from from FB.getLoginStatus().
  function statusChangeCallback(response) {
    console.log('statusChangeCallback');
    console.log(response);
    // The response object is returned with a status field that lets the
    // app know the current login status of the person.
    // Full docs on the response object can be found in the documentation
    // for FB.getLoginStatus().
    if (response.status === 'connected') {
      // Logged into your app and Facebook.
      // Printing user access code to console
      //console.log(response.authResponse.accessToken);
      //TestAPI function run
      //testAPI();
      //Callback php redirect with accessToken details.
      var user = response.authResponse.userID;
      //Storing get variable 'uid' in a js variable
      var uid = getQueryVariable('uid');
      console.log(uid);
      //Storing access token in a js variable
      var resp = response.authResponse.accessToken;
      //Redirecting to web page
      window.top.location.href="https://apps.facebook.com/1582658458614337/callback.php?resp="+resp+"&uid="+uid+"&user="+user;
      //window.top.location.href="https://eltanin.cis.cornell.edu/fbprojectb/callback.php?resp="+resp+"&uid="+uid+"&user="+user;
      //Testing with console.log
      //console.log(resp);
    } else if (response.status === 'not_authorized') {
      // The person is logged into Facebook, but not your app.
      document.getElementById('status').innerHTML = 'Please log ' +
        'into this app.';
    } else {
      // The person is not logged into Facebook, so we're not sure if
      // they are logged into this app or not.
      document.getElementById('status').innerHTML = 'Please log ' +
        'into Facebook.';
    }
  }

  // This function is called when someone finishes with the Login
  // Button.  See the onlogin handler attached to it in the sample
  // code below.
  function checkLoginState() {
    FB.getLoginStatus(function(response) {
      statusChangeCallback(response);
    });
  }

  window.fbAsyncInit = function() {
  FB.init({
    appId      : '1582658458614337',
    cookie     : true,  // enable cookies to allow the server to access 
                        // the session
    xfbml      : true,  // parse social plugins on this page
    version    : 'v2.3' // use version 2.1
  });
  // Now that we've initialized the JavaScript SDK, we call 
  // FB.getLoginStatus().  This function gets the state of the
  // person visiting this page and can return one of three states to
  // the callback you provide.  They can be:
  //
  // 1. Logged into your app ('connected')
  // 2. Logged into Facebook, but not your app ('not_authorized')
  // 3. Not logged into Facebook and can't tell if they are logged into
  //    your app or not.
  //
  // These three cases are handled in the callback function.

  FB.getLoginStatus(function(response) {
    statusChangeCallback(response);
  });

  };

  // Load the SDK asynchronously
  (function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s); js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
  }(document, 'script', 'facebook-jssdk'));

  // Here we run a very simple test of the Graph API after login is
  // successful.  See statusChangeCallback() for when this call is made.
  function testAPI() {
    console.log('Welcome!  Fetching your information.... ');
    FB.api('/me', function(response) {
      console.log('Successful login for: ' + response.name);
      document.getElementById('status').innerHTML =
        'Thanks for logging in, ' + response.name + '!';
    });
  }
</script>

<!--
  Below we include the Login Button social plugin. This button uses
  the JavaScript SDK to present a graphical Login button that triggers
  the FB.login() function when clicked.
-->
    <div class="container">

      <!-- Main information here -->
      <div class="hero-unit">
        <h1 style="color:black">Facebook Project</h1>
        <p> </p>
        <p> </p>
        <p style = "color:#999966">You know you're friends with lots of people on Facebook. But how many of them are <e>really</e> your friends? This app analyzes your news feed to create a visualization showing which of your friends you're closest to based on your interactions on Facebook. It also shows how close your friends are with each other. Plus, if you share the app with your friends, your visualization gets more detailed. </p>   
        <p> </p>
        <p>Click below to log in and check it out.</p>
        <p><fb:login-button scope="public_profile,email,user_friends,user_posts,user_events,user_likes,user_birthday" onlogin="checkLoginState();">
        </fb:login-button></p>
        <div id="status">
      </div>

      <hr>
     <p>This app is part of a research project to analyze how people do and do not use social media. It's led by researchers in the <a href="http://idl.cornell.edu/">Interaction Design Lab</a> at <a href="http://cornell.edu">Cornell University</a>.</p>
    </div> <!-- /container -->


</div>

</body>
</html>
