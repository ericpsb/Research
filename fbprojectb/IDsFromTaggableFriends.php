<?php
ini_set('display_errors', 1);
require __DIR__ . '/vendor/autoload.php';

// config
$mongopass = getenv('MONGOPASS');
$config = parse_ini_file('config.ini');
$conn_string = $config['db-conn-string1'] . $mongopass . $config['db-conn-string2'];

if (!isset($_POST['username']) || !isset($_POST['name1']) || !isset($_POST['name2']) || !isset($_POST['name3']) || !isset($_POST['name4']) || !isset($_POST['name5'])) {
    echo 'Wrong arguments\n';
    return;
}

$username = $_POST['username'];
$names = array($_POST['name1'], $_POST['name2'], $_POST['name3'], $_POST['name4'], $_POST['name5']);

$options = [];
$manager = new MongoDB\Driver\Manager($conn_string);
$readPreference = new MongoDB\Driver\ReadPreference(MongoDB\Driver\ReadPreference::RP_PRIMARY);

$ids = array();
for ($i = 0; $i < 5; $i++) {
    $filter = [
        'friend_of.0.name' => $username,
        'name' => $names[$i]
    ];
    $query = new MongoDB\Driver\Query($filter, $options);
    $friend = $manager->executeQuery($config['facebook-info-db'] . '.taggable_friends', $query, $readPreference);
    $friend = iterator_to_array($friend, false);

    if (!empty($friend[0])) {
        array_push($ids, $friend[0]->id);
    }
}

echo json_encode($ids) . "\n";
?>
