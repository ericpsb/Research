<?php

require __DIR__ . '/vendor/autoload.php';

ini_set('display_errors',1);

// get MongoDB password from environment variable
$mongopass = getenv('MONGOPASS');

// access config file
$config = parse_ini_file('config.ini');

//connect to MongoClient
$conn_string = $config['db-conn-string1'] . $mongopass . $config['db-conn-string2'];
$m = new MongoDB\Client($conn_string);

//select a database
$db = $m->selectDatabase($config['user-db']);
// $db = $m->selectDatabase('newVizTest'); // ** NEW VIZ TEST

//select a collection
$collection = $db->selectCollection('fb-users');
// $collection = $db->selectCollection('users'); // ** NEW VIZ TEST

//get pairwise interactions
//$user_interactions = new MongoCollection($db,'fb-interactions');

//get the user id from url
$userId = (isset($_GET['user'])? $_GET['user']:null);

//Plug user id to get user's json from the collection
$json = $collection->findOne(array('user id' => $userId));

// get user name
$user_name = $json['name'];

// Get list of user taggable_friends
$mongo = new MongoDB\Driver\Manager($conn_string);
$filter = ['friend_of.0.name' => $user_name];
$options = ['projection' => ['_id' => 0, 'name' => 1]];
$query = new MongoDB\Driver\Query($filter, $options);
$result = $mongo->executeQuery($config['facebook-info-db'] . '.taggable_friends', $query);
$names = array();
foreach ($result as $item) {
  array_push($names, $item->name);
}

?>

  <!DOCTYPE html>
  <html>
  <meta charset="utf-8">

  <head>
    <link rel="stylesheet" type="text/css" href="Woo10/css/animate.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/default.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/font-awesome/css/font-awesome.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/font-awesome/css/font-awesome.min.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/fontello/css/animation.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/fontello/css/fontello-codes.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/fontello/css/fontello-embedded.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/fontello/css/fontello.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/fonts.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/layout.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/media-queries.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/prettyPhoto.css">

    <script language="JavaScript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js"></script>
    <script language="JavaScript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/modernizr/2.6.2/modernizr.min.js"></script>
    <script language="JavaScript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
    <script language="JavaScript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.5/js/bootstrap.min.js"></script>
    <script language="Javascript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/URI.js/1.15.2/URI.min.js"></script>
  </head>

  <style>
    .popover {
      max-width: 320px;
      padding-top: 5px;
      padding-left: 5px;
      padding-right: 5px;
      padding-bottom: 5px;
      position: relative;
      border-radius: 50px;
    }
    
    .popover-title {
      background-color: #FFFFFF;
      font-size: 16px;
      color: #000000;
      padding-left: 10px;
      padding-top: 10px;
      padding-bottom: 10px;
      font-weight: bold;
      border-top-left-radius: 20px;
      border-top-right-radius: 20px;
    }
    
    .popover-content {
      overflow: auto;
      max-width=300px;
      max-height: 300px;
      background-color: #AE2B22;
      font-size: 17px;
      padding-left: 10px;
      padding-top: 10px;
      padding-right: 10px;
      padding-bottom: 10px;
      border-bottom-left-radius: 15px;
      border-bottom-right-radius: 15px;
      color: #FFFFFF;
    }
    
    .popover.right {
      margin-left: 25px;
    }
    
    .popover.right:before {
      content: ' ';
      height: 0;
      position: absolute;
      width: 0;
      left: -32px;
      top: 50%;
      margin-top: -18px;
      border: 20px solid transparent;
      border-right-color: #AE2B22;
    }
    
    .link {
      stroke: #999;
      stroke-width: 0.5px;
      stroke-opacity: 0.5px;
    }

    .svg-area {
      width: 100vw;
      height: 100vh;
      margin-bottom: -9px; /* seems to be necessary for some reason */
    }

    #hero {
      position: absolute;
      top: 0;
      width: 100vw;
      padding: 0;
    }

    #top5 {
      position: absolute;
      bottom: 20px;
      right: 20px;
      margin: 0;
    }
  </style>

  <body>
    <div id="fb-root"></div>

    <div id="hero">
      <h1 style="color:#FFFFFF; display:inline; float:left; margin:20px;">This is what your <i>TRUE</i> friend network looks like</h1>
      <button id="return" style="display:inline; float:left; margin: 17px;">Return to Fun Facts</button>
      <script type="text/javascript" src="viz-fb-load.js"></script>
    </div>

    <button id="top5">My Top 5 Friends</button>

    <script>
      var json = <?php echo json_encode($json); ?>; //echo user's json to this document
      var taggable_friends = <?php echo json_encode($names); ?>; // list of names of taggable_friends
    </script>
    <script type="text/javascript" src="viz-d3.js"></script>
    <script type="text/javascript" src="viz-doc.js"></script>

    <body>
