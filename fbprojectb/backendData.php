<?php
ini_set('display_errors',1);
//connect to MongoClient 
$m = new MongoClient;

//select a database
$db = $m->selectDB('fbapp-DB');

//get pairwise interactions
$user_interactions = new MongoCollection($db,'fb-interactions');

//get the user's name
$name1 = $_POST["A"];
$name2 = $_POST["B"]; 

//get the interactions of this user
$interactions = $user_interactions->findOne(array('source' => $name1,'target' => $name2 ));
if (empty($interactions)){
   $interactions = $user_interactions->findOne(array('source' => $name2,'target' => $name1 ));
}
$result = $interactions;
echo json_encode($result);



?>
