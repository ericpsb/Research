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

// $user_db = new MongoDB\Collection($db,'fb-users');
$user_db = $db->selectCollection('fb-users');

//get the user's name
$id = $_POST["A"];
$f = 'debug/debug.txt';
//file_put_contents($f, "dfdfdfd");
//get the interactions of this user
//array('user id' => $id)
$data = $user_db->findOne(array('user id' => $id));
file_put_contents($f, $id);
file_put_contents($f, json_encode($data));
$result = $data;
echo json_encode($result);
?>
