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
// TODO [P]: Delete this once it actually works the new way.
// Method with old driver:
// =======================
// $interactions = $user_interactions->find(array('source' => $name1,'target' => $name2 ));
// if (empty($interactions)){
//    $interactions = $user_interactions->find(array('source' => $name2,'target' => $name1 ));
// }
// New driver:
// ===========
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
    ],
    'limit' => 1
];

$tagid = $taggable -> findOne(array('name'=>$name2));
$tag = $tagid["id"];

// The old way:
// $interactions = $interactions ->sort(array('$natural' => -1))->limit(1);
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

if (empty($interactions)) {
    echo "null\n";
}
else {
    $result = (array) $interactions[0];
    $result["tag"] = $tag;
    $result = json_encode($result);
    echo $result . "\n";
}
?>
