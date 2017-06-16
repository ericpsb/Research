<?php
ini_set('display_errors', 1);
require __DIR__ . '/vendor/autoload.php';

// config
$mongopass = getenv('MONGOPASS');
$config = parse_ini_file('config.ini');
$conn_string = $config['db-conn-string1'] . $mongopass . $config['db-conn-string2'];

if (!isset($_POST['name'])) {
    echo "user not found\n";
    return;
}

$name = $_POST["name"];

// query for user nodes and links
$filter = [
    'name' => $name
];
$options = [];

$query = new MongoDB\Driver\Query($filter, $options);
$manager = new MongoDB\Driver\Manager($conn_string);
$readPreference = new MongoDB\Driver\ReadPreference(MongoDB\Driver\ReadPreference::RP_PRIMARY);

$interactions = $manager->executeQuery($config['user-db'] . '.fb-users', $query, $readPreference);
$interactions = iterator_to_array($interactions, false);
$links = $interactions[0]->json->links;

// filter only user's friends
$myFriendLinks = array_filter($links, 'isMyFriend');

// sort by link strength
usort($myFriendLinks, 'cmpLink');

// return names of top 5 friends
$nodes = $interactions[0]->json->nodes;
foreach (array_slice($myFriendLinks, 0, 5) as $link) {
    echo $nodes[$link->target]->name . "\n";
}

return;



// functions
function isMyFriend($link) {
    return $link->source == 0;
}

function cmpLink($a, $b) {
    return $b->value - $a->value;
}
?>
