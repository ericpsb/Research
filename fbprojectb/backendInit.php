<?php
ini_set('display_errors',1);
//connect to MongoClient 
$m = new MongoClient("localhost:27017");

//select a database
$db = $m->selectDB('fbapp-DB');

$user_db = new MongoCollection($db,'fb-users');

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
