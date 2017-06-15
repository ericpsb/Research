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
    <link rel="stylesheet" type="text/css" href="viz-styles.css">

    <script language="JavaScript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js"></script>
    <script language="JavaScript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/modernizr/2.6.2/modernizr.min.js"></script>
    <script language="JavaScript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
    <script language="JavaScript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.5/js/bootstrap.min.js"></script>
    <script language="Javascript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/URI.js/1.15.2/URI.min.js"></script>
    <script src="https://use.fontawesome.com/d366671606.js"></script>
  </head>

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

    <div id="popUpVeil"></div>
    <div id="topFiveWindow">
      <div id="closeButton">
        <button id="closeTopFive">
          <i class="fa fa-times fa-lg" aria-hidden="true"></i>
        </button>
      </div>

      <h1 class="center-title">Your Top 5 Friends</h1>
      <hr>

      <div id="panel-1">
        <table id="top-table">
          <tr class="top-5-item">
            <td class="name-number">1</td>
            <td id="p1-img" class="name-img"></td>
            <td id="p1-name" class="name">Lumber (wood)</td>
          </tr>

          <tr class="top-5-item">
            <td class="name-number">2</td>
            <td id="p2-img" class="name-img"></td>
            <td id="p2-name" class="name">Brick (clay)</td>
          </tr>

          <tr class="top-5-item">
            <td class="name-number">3</td>
            <td id="p3-img" class="name-img"></td>
            <td id="p3-name" class="name">Grain (wheat)</td>
          </tr>

          <tr class="top-5-item">
            <td class="name-number">4</td>
            <td id="p4-img" class="name-img"></td>
            <td id="p4-name" class="name">Wool (sheep)</td>
          </tr>

          <tr class="top-5-item">
            <td class="name-number">5</td>
            <td id="p5-img" class="name-img"></td>
            <td id="p5-name" class="name">Ore (stone)</td>
          </tr>

          <tr class="top-5-item">
            <td class="name-number">6</td>
            <td id="p6-img" class="name-img"></td>
            <td id="p6-name" class="name">Tihmothy Berrill</td>
          </tr>
        </table>

        <button id="post-top-5">Post About This on Facebook</button>
      </div>

      <div id="top-post">
        This is where a text box for sharing with friends will be, plus a button to post with.
      </div>
    <body>
