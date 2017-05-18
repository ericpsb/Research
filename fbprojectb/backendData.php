<?php
ini_set('display_errors',1);
//connect to MongoClient 
require __DIR__ . '/vendor/autoload.php';
$m = new MongoDB\Client("mongodb://localhost:27017");

//select a database
$db = $m->selectDatabase('fbapp-DB');
$db2 = $m->selectDatabase('fb_nonuse_Nov_20');

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
$manager = new MongoDB\Driver\Manager('mongodb://localhost:27017');
$readPreference = new MongoDB\Driver\ReadPreference(MongoDB\Driver\ReadPreference::RP_PRIMARY);

$interactions = $manager->executeQuery('fbapp-DB.fb-interactions', $query, $readPreference);
$interactions = iterator_to_array($interactions,false);

if (empty($interactions)) {
    $query = new MongoDB\Driver\Query($filterReverse, $options);
    $interactions = $manager->executeQuery('fbapp-DB.fb-interactions', $query, $readPreference);
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
