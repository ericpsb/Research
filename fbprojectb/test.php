<?php 
$m = new MongoClient;
$m->test->test->insert(array('foo'=>'bar'));

?>
