<?php
ini_set('display_errors', 1);

// get access token and uid from URL parameters
$access_token = !empty($_GET['resp']) ? $_GET['resp'] : NULL;

//Need to capture uid variable from the HTTP GET variable
// $uid = !empty($_GET['uid']) ? $_GET['uid'] : NULL;
$uid = !empty($_GET['user']) ? $_GET['user'] : NULL;

// run backend scripts to get long term token and scrape/process data
$command = escapeshellcmd("./ltget.py $access_token");
$output = shell_exec("echo '" . $command . "' | at now");
// echo $output; // instead of having this output, maybe just log properly?

?>
  <html>

  <head>
    <title>Facebook Login Successful!</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">

    <!-- Le styles -->
    <link href="bootstrap.css" rel="stylesheet">
    <style type="text/css">
      body {
        padding-top: 60px;
        padding-bottom: 40px;
      }
    </style>
    <link rel="stylesheet" type="text/css" href="Woo10/css/animate.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/default.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/font-awesome/css/font-awesome.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/font-awesome/css/font-awesome.min.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/fontello/css/animation.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/fontello/css/fontello-codes.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/fontello/css/fontello-embedded.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/fontello/css/fontello-ie7-codes.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/fontello/css/fontello-ie7.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/fontello/css/fontello.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/fonts.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/layout.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/media-queries.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/prettyPhoto.css">
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
    <script language="JavaScript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
  </head>

  <body>

    <div class="container">

      <!-- Main information here -->
      <div class="hero-unit">
        <h1 style="color:#11ABB0">Facebook Login Successful!</h1>
        <p> </p>
        <p> </p>
        <p style="font-weight:bold">Thank you for allowing us access to your Facebook usage data.</p>
        <p style="font-weight:bold">Please help the research by sharing this app with your friends.</p>
        <button id="viz-button">Proceed to Visualization</button>
        <script type="text/javascript">
          function getParamByName(name) {
            name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
            var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
              results = regex.exec(window.location.search);
            return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
          }
          window.fbAsyncInit = function() {
            FB.init({
              appId: '1582658458614337',
              cookie: true, // enable cookies to allow the server to access
              // the session
              xfbml: true, // parse social plugins on this page
              version: 'v2.9' // use version 2.9
            });
          };


          var uid = getParamByName("user");
          console.log(uid);

          $.post('backendInit.php', {
            A: uid
          }, function(result) {
            var domain = "https://das-lab.org/";
            var userdbdata = JSON.parse(result);
            if (userdbdata != null && userdbdata["json"]) {
              document.getElementById("viz-button").onclick = function() {
                window.top.location.href = domain + "truefriend/viz.php?resp=" + getParamByName('resp') + "&user=" + getParamByName('user');
              }
            } else {
              document.getElementById("viz-button").onclick = function() {
                window.top.location.href = domain + "truefriend/initViz.php?resp=" + getParamByName('resp') + "&user=" + getParamByName('user');
              };
            }
          });
        </script>
      </div>
    </div>
    <!-- /container -->


    </div>

  </body>

  </html>
