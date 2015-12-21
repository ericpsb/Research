<?php
ini_set('display_errors',1);
//connect to MongoClient 
$m = new MongoClient;

//select a database
$db = $m->selectDB('fbapp-DB');

$user_db = new MongoCollection($db,'fb-user');

//get the user's name
$id = $_POST["A"];
//get the interactions of this user
$data = $user_db->findOne(array('user id' => $id));
$result = $data;
echo json_encode($result);
?>

