<?php
ini_set('display_errors',1);
require __DIR__ . '/vendor/autoload.php';

// get MongoDB password from environment variable
$mongopass = getenv('MONGOPASS');

// access config file
$config = parse_ini_file('config.ini');

//connect to MongoClient
$conn_string = $config['db-conn-string1'] . $mongopass . $config['db-conn-string2'];
$m = new MongoDB\Client($conn_string);

//select a database
$db = $m->selectDatabase($config['user-db']);
$db2 = $m->selectDatabase($config['facebook-info-db']);

// get user access token
$access_token = isset($_POST["C"]) ? $_POST["C"] : null;

//get pairwise interactions
$user_interactions = $db->selectCollection('fb-interactions');
$taggable = $db2->selectCollection('taggable_friends');

//get the users' name
$name1 = isset($_POST["A"]) ? $_POST["A"] : null;
$name2 = isset($_POST["B"]) ? $_POST["B"] : null; 

//get the interactions of this user
$filter = [
    'source' => $name1,
    'target' => $name2
];
$filterReverse = [
    'source' => $name2,
    'target' => $name1
];
$options = [
    // 'sort' => [
    //     '$natural' => -1
    // ]
];

$tagid = $taggable -> findOne(array('name'=>$name2));
$tag = $tagid["id"];

$query = new MongoDB\Driver\Query($filter, $options);
$manager = new MongoDB\Driver\Manager($conn_string);
$readPreference = new MongoDB\Driver\ReadPreference(MongoDB\Driver\ReadPreference::RP_PRIMARY);

$interactions = $manager->executeQuery($config['user-db'] . '.fb-interactions', $query, $readPreference);
$interactions = iterator_to_array($interactions,false);

if (empty($interactions)) {
    $query = new MongoDB\Driver\Query($filterReverse, $options);
    $interactions = $manager->executeQuery($config['user-db'] . '.fb-interactions', $query, $readPreference);
    $interactions = iterator_to_array($interactions,false);
}

$result = "null";

if (!empty($interactions)) {
    foreach ($interactions as $item) {
        $itemAsArray = (array) $item;
        if (!empty($itemAsArray['data'])) {
            // Loop through ['data'], grab id in second spot if photo, post, or status, and make request to get "picture"
            $itemAsArray['data'] = array_map("resolvePicture", $itemAsArray['data']);

            // sort by date
            usort($itemAsArray['data'], 'compare');

            $result = $itemAsArray;
            $result["tag"] = $tag;
            $result = json_encode($result);
            break;
        }
    }
}

echo $result . "\n";

function resolvePicture(array $post) {
    if ($post[0] == 'photo') {
        $post[2] = requestPicture($post[2]);
    }
    elseif ($post[0] == 'post' || $post[0] == 'status') {
        $post[7] = requestPicture($post[7]);
    }
    return $post;
}

function requestPicture($id) {
    global $access_token;
    $ch = curl_init("https://graph.facebook.com/v2.9/$id?fields=picture&access_token=$access_token");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    $data = curl_exec($ch);
    curl_close($ch);
    $dataJson = json_decode($data, true);
    if (isset($dataJson['picture'])) {
        return $dataJson['picture'];
    }
    else {
        return "";
    }
}

function compare($a, $b) {
    $adate = date('Y-m-d', strtotime($a[count($a)-1]));
    $bdate = date('Y-m-d', strtotime($b[count($b)-1]));
    return -1 * strcmp($adate, $bdate);
}
?>
