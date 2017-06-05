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

//get pairwise interactions
$user_interactions = $db->selectCollection('fb-interactions');
$taggable = $db2->selectCollection('taggable_friends');
//get the user's name
$name1 = $_POST["A"];
$name2 = $_POST["B"]; 

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
    'sort' => [
        '$natural' => -1
    ]
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
        if (!empty($itemAsArray["data"])) {
            $result = $itemAsArray;
            $result["tag"] = $tag;
            $result = json_encode($result);
            break;
        }
    }
}

echo $result . "\n";
?>
