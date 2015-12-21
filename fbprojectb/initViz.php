<?php
ini_set('display_errors',1);
//get the user id from url
ini_set("max_execution_time",2000);
$accessToken = (isset($_GET['resp'])? $_GET['resp']:null);
$user = (isset($_GET['user'])? $_GET['user']:null);
$output = shell_exec("python initViz.py " . escapeshellarg(json_encode($user)) . " 2>&1");
?>

<!DOCTYPE html>
<html>
<meta charset="utf-8">
<head>
<link rel="stylesheet" type ="text/css" href="Woo10/css/animate.css">
<link rel="stylesheet" type ="text/css" href="Woo10/css/default.css">
<link rel="stylesheet" type ="text/css" href="Woo10/css/font-awesome/css/font-awesome.css">
<link rel="stylesheet" type ="text/css" href="Woo10/css/font-awesome/css/font-awesome.min.css">
<link rel="stylesheet" type ="text/css" href="Woo10/css/fontello/css/animation.css">
<link rel="stylesheet" type ="text/css" href="Woo10/css/fontello/css/fontello-codes.css">
<link rel="stylesheet" type ="text/css"  href="Woo10/css/fontello/css/fontello-embedded.css"> 
<link rel="stylesheet" type ="text/css"  href="Woo10/css/fontello/css/fontello.css">
<link rel="stylesheet" type ="text/css" href="Woo10/css/fonts.css">
<link rel="stylesheet" type ="text/css"  href="Woo10/css/layout.css">
<link rel="stylesheet" type ="text/css"  href="Woo10/css/media-queries.css">
<link rel="stylesheet" type ="text/css" href="Woo10/css/prettyPhoto.css">
<script language="JavaScript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js"></script>
<script language="JavaScript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/modernizr/2.6.2/modernizr.min.js"></script>
<script language="JavaScript" type="text/javascript" src="https:////cdnjs.cloudflare.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
<script language="JavaScript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.5/js/bootstrap.min.js"></script>
<script language="Javascript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/URI.js/1.15.2/URI.min.js"></script>
</head>
<script type="text/javascript" src="blast/jquery.blast.min.js"></script>
<p></p>
<p></p>
<p></p>
<p></p>
<div id = "hero">
<h4 style="color:#8585ad">   Most Recent Post on your Timeline</h1>
<h6 id = "first" style="color:#FFFFFF"></h4> 
<p></p>
<h4 style="color:#8585ad">   Oldest post on your Timeline</h3>
<h6 id = "last" style="color:#FFFFFF"></h4> 
<p></p>
<h4 style="color:#8585ad">   Total number of friends</h3>
<h6 id = "numf" style="color:#FFFFFF"></h4>
<p></p>
<h4 style="color:#8585ad">   Total number of Events Attended</h3> 
<h6 id = "nume" style="color:#FFFFFF"></h4> 
</div>
<script>
var x  = <?php echo json_encode($output); ?>;
var json = JSON.parse(x);
document.getElementById("first").innerHTML = "   " +json["first"][0] + " on "+json["first"][1];
document.getElementById("last").innerHTML = "   " + json["last"][0] + " on "+json["last"][1] ; 
document.getElementById("numf").innerHTML = "   " + json["friends"]
document.getElementById("nume").innerHTML = "   " + json["events"]
</script>
<h4 style="color:#8585ad">   Please wait while we generate your visualization. We will notify you when it is ready.</h3> 
<p></p>
<button id="Viz Button" type="submit" disabled>Visualization</button>
<script>
var x  = <?php echo json_encode($user); ?>;
var uid = JSON.parse(x);
console.log(uid);
$.post('backendInit.php', { A : uid},function(result){
var userdata = $.parseJSON(result);
console.log(userdata);
if (userdata["json"]) {
  document.getElementById("Viz button").disabled = false;
  document.getElementById("Viz Button").onclick = function(){
                //window.top.location.href="https://eltanin.cis.cornell.edu/fbprojectb/initViz.php?resp="+getParamByName('resp')+"&user="+getParamByName('user');
                window.top.location.href="https://apps.facebook.com/1582658458614337/viz.php?resp="+getParamByName('resp')+"&user="+getParamByName('user');
}
}});
</script>
