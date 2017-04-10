<?php

require __DIR__ . '/vendor/autoload.php';
ini_set('display_errors', 1);

//First generate the data array to be plugged into the d3 visualization

#Fetching the GET variables
$accessToken = (isset($_GET['resp'])? $_GET['resp']:null);
$userid = (isset($_GET['user'])? $_GET['user']:null);

#Birthday must be in mm/dd/yyyy format
function getAge($birthday){
    $birthday = explode("/", $birthday);
    $age = (date("md", date("U", mktime(0, 0, 0, $birthday[0], $birthday[1], $birthday[2]))) > date("md") ? ((date("Y") - $birthday[2]) - 1) : (date("Y") - $birthday[2]));
    return $age;
};

function getUserData($accessToken){
    #Generating FB Graph API request urls
    $fb = "https://graph.facebook.com/v2.8/me?fields=";
    $me_field = 'id,name,first_name,last_name,birthday,email,gender';
    $friends_field = "friends.limit(1)";
    
    #Fetching user data
    $url = $fb . $me_field . "," . $friends_field . '&access_token=' . $accessToken;
    $result = file_get_contents($url);
    $array = json_decode($result,true);
    
    $array["age"] = getAge($array["birthday"]);
    
    return json_encode($array);
}





function getDBdata(){
    $client = new MongoDB\Client("mongodb://localhost:27017");
    $db = $client->selectDatabase("fb_nonuse_Nov_20");
    $collection = $db->selectCollection('user');
    
    #Setting
    $query = array('total_friends' => array( '$exists' => true ));
    $fields = array('total_friends' => true, '_id' => false, 'birthday' => true, 'gender' => true);
    $cursor = $collection->find($query, $fields);
    $array = iterator_to_array($cursor);
    $array2 = [];
    foreach ($array as $key => $value) {
		if (!empty($value["birthday"])) {
			$value["age"] = getAge($value["birthday"]);
		}
		array_push($array2, $value);
    };
    
    return json_encode($array2);
}

$dbdata = getDBdata();
$profile = getUserData($accessToken);
$user = json_decode($profile,true);

$firstname = $user["first_name"];
$friendscount = $user['friends']['summary']['total_count'];
$age = $user["age"];
// $percentage = "90%";
if ($friendscount > 350) {
    $compare = "more than";
} elseif($friendscount < 350){
    $compare = "less than";
} else{
    $compare = "equal to";
}

$email = $user["email"];
$birthday = $user["birthday"];


// $dbarray = getDBdata();

// $func = function($value) {
//    	return getAge($value["birthday"]);
// };


// $dbage = array_map($func, $getDBdata);




?>


  <!DOCTYPE html>
  <html>

  <head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <link rel="stylesheet" type="text/css" href="Woo10/css/animate.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/default.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/font-awesome/css/font-awesome.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/font-awesome/css/font-awesome.min.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/fontello/css/animation.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/fontello/css/fontello-codes.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/fontello/css/fontello-embedded.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/fontello/css/fontello.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/fonts.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/layout.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/media-queries.css">
    <link rel="stylesheet" type="text/css" href="Woo10/css/prettyPhoto.css">
    <script language="JavaScript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js"></script>
    <script language="JavaScript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/modernizr/2.6.2/modernizr.min.js"></script>
    <script language="JavaScript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
    <script language="JavaScript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.5/js/bootstrap.min.js"></script>
    <script language="Javascript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/URI.js/1.15.2/URI.min.js"></script>
    <script language="Javascript" type="text/javascript" src="https://cdnjs.cloudflare.com/ajax/libs/d3-legend/1.12.0/d3-legend.min.js"></script>

    <style>
      .container-fluid {
        margin-top: 50px;
        padding: 0;
      }
      
      form {
        color: #ddd;
      }
      
      .text {
        margin-top: 11%;
      }
      
      .bar {
        fill: #3399FF;
        opacity: 0.5;
      }
      
      .bar:hover {
        fill: brown;
      }
      
      .axis {
        stroke: #ddd;
        font: 10px sans-serif;
      }
      
      .axis path,
      .axis line {
        fill: none;
        stroke: #ddd;
        shape-rendering: crispEdges;
      }
      
      .x.axis path {
        display: none;
      }
      
      .graph1 {
        stroke: #ddd;
        stroke-width: 3px;
      }
      
      text.label {
        fill: #ddd;
      }
      
      .graph3 {
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        width: 960px;
        height: 500px;
        position: relative;
      }
      
      .graph3 svg {
        width: 100%;
        height: 100%;
        position: center;
      }
      
      .graph3 path.slice {
        stroke-width: 2px;
      }
      
      .graph3 text {
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
      }
      
      .graph3 polyline {
        opacity: .3;
        stroke: black;
        stroke-width: 2px;
        fill: none;
      }
      
      .labelValue {
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 60%;
        opacity: .5;
      }
      
      label {
        display: inline;
        font-size: 14px;
        color: #ddd;
      }
      
      .toolTip {
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        position: absolute;
        display: none;
        width: auto;
        height: auto;
        background: none repeat scroll 0 0 white;
        border: 0 none;
        border-radius: 8px 8px 8px 8px;
        box-shadow: -3px 3px 15px #888888;
        color: black;
        font: 12px sans-serif;
        padding: 5px;
        text-align: center;
      }
      
      .legend {
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        font-size: 60%;
      }
    </style>
  </head>

  <body>
    <div class="container-fluid">
      <script>
        //generate front end datafields

        var dbdata = <?php echo $dbdata; ?>;
        var user = <?php echo $profile; ?>;
        console.log(user);

        var userfriend = user['friends']['summary']['total_count'];

        var birthday = user['birthday'];

        var dbfriendarray = dbdata.map(function(d) {
          return d.total_friends;
        }).sort(function(a, b) {
          return a - b;
        });

        function morefriendsthan(array, value) {
          var i = 0;
          while (array[i] < value && i < array.length) {
            i++;
          }
          return i / array.length;
        }

        function birthdayformat(birthday) {
          var mydate = new Date(birthday);
          var month = ["January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
          ][mydate.getMonth()];
          var str = month + ' ' + mydate.getDate() + ', ' + mydate.getFullYear();
          return str;
        }

        var percentage = morefriendsthan(dbfriendarray, userfriend);
        var percentagetext = (percentage * 100).toFixed(1) + "%";
      </script>

      <div class="row">
        <div class="header col-xs-12 col-sm-10 offset-sm-2">
          <h1 style="color:#fff">Hi <?php echo $firstname; ?>!</h1>
          <br>

          <h3 style="color:#c2c2d6">Thanks for using our app! Normally it will take us about 20 minutes to gather all the information we need and generate your Social Interaction Graph. We will notify you through email when it is ready. In the mean time, here are some fun facts about your number of friends on Facebook:</h4>
    <br>
<h5 style="color:#a3a3c2"> · You have <?php echo $friendscount;?> friends, which is <?php echo $compare;?> the world average of 350. Keep it up!</h4>
<h5 style="color:#9494b8"> · Your birthday is <span id="birthday"></span>.</h4>
<h5 style="color:#8585ad"> · Your email address is <?php echo $email;?>. Please remember to check your emails often! We will send notification to this email address when your visualization is ready.</h4>
<br>
</div>
</div>

<div class="row">
<div id = "graph1" class = "col-xs-12 col-sm-6"></div>
<div class="col-xs-12 col-sm-6 text">
<h5 id = "first" style="color:#8585ad">How many more friends do you have compared to other people in our database?</h5>
</div>
<script>
$("#percentage").html(percentagetext);
</script>



<script>
$('#birthday').html(birthdayformat(birthday));

var tau = 2 * Math.PI;

var margin2 = {top: 20, right: 20, bottom: 80, left: 20};
width2 = 400 - margin2.left - margin2.right;
height2 = 400 - margin2.top - margin2.bottom;

var chart = d3.select("#graph1")
.append('svg')
.attr("width", width2 + margin2.left + margin2.right)
.attr("height", height2 + margin2.top + margin2.bottom)
.append("g")
.attr("transform", "translate(" + ((width2/2)+margin2.left) + "," + ((height2/2)+margin2.top) + ")");




var radius = Math.min(width2, height2) / 2;

// var color = d3.scale.ordinal()
// 	.range(["#3399FF", "#5DAEF8", "#86C3FA", "#ADD6FB", "#D6EBFD"]);

var arc = d3.svg.arc()
.outerRadius(radius)
.innerRadius(radius - 20)
.startAngle(0);

var background = chart.append("path")
.datum({endAngle: tau})
.style("fill", "#ddd")
.attr("d", arc);

var foreground = chart.append("path")
.datum({endAngle: 0})
.style("fill", "#5DAEF8")
.attr("d", arc);

foreground.transition()
.duration(1000)
.attrTween("d", arcTween(percentage * tau));

chart.append("text").attr("x","10").attr("y","20").attr("text-anchor","middle")
.attr("font-size","50px").attr("fill","#ddd").text(percentagetext);

var ordinal = d3.scale.ordinal()
.domain(["a", "b", "c", "d", "e"])
.range([ "rgb(153, 107, 195)", "rgb(56, 106, 197)", "rgb(93, 199, 76)", "rgb(223, 199, 31)", "rgb(234, 118, 47)"]);


var ordinal = d3.scale.ordinal()
.domain(["People who have fewer friends than you", "People who have more friends than you"])
.range([ "#5DAEF8", "#ddd"]);



chart.append("g")
.attr("class", "legendOrdinal")
.attr("transform", "translate(-110,170)");

var legendOrdinal = d3.legend.color()
.shapePadding(10)
.scale(ordinal);

chart.select(".legendOrdinal")
.call(legendOrdinal);


function arcTween(newAngle) {
    
    return function(d) {
        
        var interpolate = d3.interpolate(d.endAngle, newAngle);
        
        return function(t) {
            
            d.endAngle = interpolate(t);
            return arc(d);
        };
    };
}





</script>
</div>
<div class="row">
<div class="col-xs-12 col-sm-6 text">
<h5 style="color:#8585ad"> What about comparing your number of friends with the average by gender in our database?</h5>
</div>
<div id = "graph2" class = "col-xs-12 col-sm-6"></div>







<script>
var male = [],female = [], other = [];

for(var i=0;i<dbdata.length;i++){
    if(dbdata[i].gender == "male"){
        male.push(dbdata[i].total_friends);
    }
    else if(dbdata[i].gender == "female"){
        female.push(dbdata[i].total_friends);
    }
    else{
        other.push(dbdata[i].total_friends);
    }
}

var malemean = male.length > 0 ? d3.mean(male):0;
var femalemean = female.length > 0 ? d3.mean(female):0;
var othermean = other.length > 0 ? d3.mean(other):0;

dataset0 = [{"gender" : "Male", "friends":malemean},{"gender":"Female", "friends":femalemean},{"gender":"Other","friends":othermean}];


// Mike Bostock "margin conventions"
var margin3 = {top: 20, right: 20, bottom: 30, left: 30},
width3 = 500 - margin3.left - margin3.right,
height3 = 300 - margin3.top - margin3.bottom;

var svg3 = d3.select("#graph2").append("svg")
.attr("width", width3 + margin3.left + margin3.right)
.attr("height", height3 + margin3.top + margin3.bottom)
.append("g")
.attr("transform", "translate(" + margin3.left + "," + margin3.top + ")");

svg3.append("g")
.attr("class", "x axis")
.attr("transform", "translate(0," + height3 + ")")

svg3.append("g")
.attr("class", "y axis")
.append("text") // just for the title (ticks are automatic)
.attr("transform", "rotate(-90)") // rotate the text!
.attr("y", 6)
.attr("dy", ".71em")
.style("text-anchor", "end")
.text("Number of Friends");

var div = d3.select("body").append("div").attr("class", "toolTip");

replay1(dataset0);

function replay1(data) {
    var slices = [];
    for (var i = 0; i < data.length; i++) {
        slices.push(data.slice(0, i+1));
    }
    slices.forEach(function(slice, index){
        setTimeout(function(){
            draw1(slice);
        }, index * 300);
    });
}

function draw1(data) {
    var usergender = user["gender"];
    console.log(usergender);
    var userfriend = <?php echo $friendscount;?>;
    var usergenderrange;
    if(usergender == "male"){
        usergenderrange = "Male";
    } else if(usergender == "female"){
        usergenderrange = "Female";
    } else{
        usergenderrange = "Other";
    };
    
    // measure the domain (for x, unique letters) (for y [0,maxFrequency])
    // now the scales are finished and usable
    var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], .5).domain(data.map(function(d) { return d.gender; }));
    var y = d3.scale.linear()
    .range([height, 0]).domain([0, Math.max(userfriend, d3.max(data, function(d) { return d.friends; }))]);
    
    var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");
    
    var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")
    .ticks(10);
    
    // another g element, this time to move the origin to the bottom of the svg element
    // someSelection.call(thing) is roughly equivalent to thing(someSelection[i])
    //   for everything in the selection\
    // the end result is g populated with text and lines!
    svg3.select('.x.axis').transition().duration(300).call(xAxis);
    
    // same for yAxis but with more transform and a title
    svg3.select(".y.axis").transition().duration(300).call(yAxis)
    
    // THIS IS THE ACTUAL WORK!
    var bars = svg3.selectAll(".bar").data(data, function(d) { return d.gender; }) // (data) is an array/iterable thing, second argument is an ID generator function
    
    bars.exit()
    .transition()
    .duration(300)
    .attr("y", y(0))
    .attr("height", height3 - y(0))
    .style('fill-opacity', 1e-6)
    .remove();
    
    // data that needs DOM = enter() (a set/selection, not an event!)
    bars.enter().append("rect")
    .attr("class", "bar")
    .attr("y", y(0))
    .attr("height", height3 - y(0));
    
    // the "UPDATE" set:
    bars.transition().duration(300).attr("x", function(d) { return x(d.gender); }) // (d) is one item from the data array, x is the scale object from above
    .attr("width", x.rangeBand()) // constant, so no callback function(d) here
    .attr("y", function(d) { return y(d.friends); })
    .attr("height", function(d) { return height3 - y(d.friends); }); // flip the height, because y's domain is bottom up, but SVG renders top down
    
    bars
    .on("mousemove", function(d){
        div.style("left", d3.event.pageX+10+"px");
        div.style("top", d3.event.pageY-25+"px");
        div.style("display", "inline-block");
        div.html((d.gender)+"<br>"+(d.friends)+" Friends");
    });
    bars
    .on("mouseout", function(d){
        div.style("display", "none");
    });
    
    if(data.length == 3){
        setTimeout(function() {
            svg3.append("line").attr("x1",x(usergenderrange))
            .attr("y1", y(userfriend))
            .attr("x2", x(usergenderrange)+x.rangeBand())
            .attr("y2",y(userfriend))
            .attr("stroke", "white");
            
            
            
            svg3.append("text").attr("x", x(usergenderrange)+ x.rangeBand()/2).attr("y", y(userfriend) + 20)
            .attr("text-anchor","middle").text("You are here").attr("fill","white");
            
        }, 500);
    };
}

</script>
</div>
<div class="row">




<div id = "graph3" class = "col-xs-12 col-sm-6">
<!-- <form>
<label><input type="radio" name="dataset" id="dataset" value="total" checked> Total</label>
<label><input type="radio" name="dataset" id="dataset" value="option1"> Male</label>
<label><input type="radio" name="dataset" id="dataset" value="option2"> Female</label>
</form> -->
</div>
<div class="col-xs-12 col-sm-6 text">
<h5 style="color:#8585ad; padding-left :20px">Finally, here's the average number of Facebook friends by age in the United States. How do you compare to other people of the same age?</h5>
</div>

<script>


//first graph
var data1 = [{"age":"12-17", "friends" : 521},{"age":"18-24", "friends" : 649},{"age":"25-34", "friends" : 360},{"age":"35-44", "friends" : 277},{"age":"45-54", "friends" : 220},{"age":"55-64", "friends" : 129},{"age":"65+", "friends" : 102},{"age":"Average", "friends" : 350}];



// Mike Bostock "margin conventions"
var margin = {top: 20, right: 20, bottom: 30, left: 30},
width = 500 - margin.left - margin.right,
height = 300 - margin.top - margin.bottom;

var svg = d3.select("#graph3").append("svg")
.attr("width", width + margin.left + margin.right)
.attr("height", height + margin.top + margin.bottom)
.append("g")
.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

svg.append("g")
.attr("class", "x axis")
.attr("transform", "translate(0," + height + ")")

svg.append("g")
.attr("class", "y axis")
.append("text") // just for the title (ticks are automatic)
.attr("transform", "rotate(-90)") // rotate the text!
.attr("y", 6)
.attr("dy", ".71em")
.style("text-anchor", "end")
.text("Number of Friends");

var div = d3.select("body").append("div").attr("class", "toolTip");

replay(data1);


function type(d) {
    // + coerces to a Number from a String (or anything)
    d.frequency = +d.frequency;
    return d;
}

function replay(data) {
    var slices = [];
    for (var i = 0; i < data.length; i++) {
        slices.push(data.slice(0, i+1));
    }
    slices.forEach(function(slice, index){
        setTimeout(function(){
            draw(slice);
        }, index * 300);
    });
}

function draw(data) {
    var userage = <?php echo $age;?>;
    var userfriend = <?php echo $friendscount;?>;
    var useragerange;
    if(userage >=12 && userage <18){
        useragerange = "12-17";
    } else if(userage >=18 && userage < 25){
        useragerange = "18-24";
    } else if(userage >=25 && userage < 35){
        useragerange = "25-34";
    } else if(userage >=35 && userage < 45){
        useragerange = "35-44";
    } else if(userage >=45 && userage < 55){
        useragerange = "45-54";
    } else if(userage >=55 && userage < 65){
        useragerange = "55-64";
    } else{
        useragerange = "65+";
    };
    
    // measure the domain (for x, unique letters) (for y [0,maxFrequency])
    // now the scales are finished and usable
    var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], .1).domain(data.map(function(d) { return d.age; }));
    var y = d3.scale.linear()
    .range([height, 0]).domain([0, Math.max(userfriend, d3.max(data, function(d) { return d.friends; }))]);
    
    var xAxis = d3.svg.axis()
    .scale(x)
    .orient("bottom");
    
    var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")
    .ticks(10);
    
    // another g element, this time to move the origin to the bottom of the svg element
    // someSelection.call(thing) is roughly equivalent to thing(someSelection[i])
    //   for everything in the selection\
    // the end result is g populated with text and lines!
    svg.select('.x.axis').transition().duration(300).call(xAxis);
    
    // same for yAxis but with more transform and a title
    svg.select(".y.axis").transition().duration(300).call(yAxis)
    
    // THIS IS THE ACTUAL WORK!
    var bars = svg.selectAll(".bar").data(data, function(d) { return d.age; }) // (data) is an array/iterable thing, second argument is an ID generator function
    
    bars.exit()
    .transition()
    .duration(300)
    .attr("y", y(0))
    .attr("height", height - y(0))
    .style('fill-opacity', 1e-6)
    .remove();
    
    // data that needs DOM = enter() (a set/selection, not an event!)
    bars.enter().append("rect")
    .attr("class", "bar")
    .attr("y", y(0))
    .attr("height", height - y(0));
    
    // the "UPDATE" set:
    bars.transition().duration(300).attr("x", function(d) { return x(d.age); }) // (d) is one item from the data array, x is the scale object from above
    .attr("width", x.rangeBand()) // constant, so no callback function(d) here
    .attr("y", function(d) { return y(d.friends); })
    .attr("height", function(d) { return height - y(d.friends); }); // flip the height, because y's domain is bottom up, but SVG renders top down
    
    bars
    .on("mousemove", function(d){
        div.style("left", d3.event.pageX+10+"px");
        div.style("top", d3.event.pageY-25+"px");
        div.style("display", "inline-block");
        div.html((d.age)+"<br>"+(d.friends)+" Friends");
    });
    bars
    .on("mouseout", function(d){
        div.style("display", "none");
    });
    
    if(data.length == 8){
        setTimeout(function() {
            svg.append("line").attr("x1",x(useragerange))
            .attr("y1", y(userfriend))
            .attr("x2", x(useragerange)+x.rangeBand())
            .attr("y2",y(userfriend))
            .attr("stroke", "white");
            
            svg.append("line").attr("x1",x("Average"))
            .attr("y1", y(userfriend))
            .attr("x2", x("Average")+x.rangeBand())
            .attr("y2",y(userfriend))
            .attr("stroke", "white");
            
            svg.append("text").attr("x", x(useragerange)+ x.rangeBand()/2).attr("y", y(userfriend) + 20)
            .attr("text-anchor","middle").text("You are here").attr("fill","white");
            
        }, 500);
    };
}



//  datasetTotal = [
//      {"age":"12-17", "friends" : 0},{"age":"18-24", "friends" : 420},{"age":"25-34", "friends" : 190},{"age":"35-44", "friends" : 0},{"age":"45-54", "friends" : 0},{"age":"55-64", "friends" : 0},{"age":"65+", "friends" : 0},{"age":"Average", "friends" : 343}
//  ];

//  datasetOption1 = [
//       {"age":"12-17", "friends" : 0},{"age":"18-24", "friends" : 490},{"age":"25-34", "friends" : 190},{"age":"35-44", "friends" : 0},{"age":"45-54", "friends" : 0},{"age":"55-64", "friends" : 0},{"age":"65+", "friends" : 0},{"age":"Average", "friends" : 340}
//  ];

//  datasetOption2 = [
//         {"age":"12-17", "friends" : 0},{"age":"18-24", "friends" : 350},{"age":"25-34", "friends" : 0},{"age":"35-44", "friends" : 0},{"age":"45-54", "friends" : 0},{"age":"55-64", "friends" : 0},{"age":"65+", "friends" : 0},{"age":"Average", "friends" : 350}
//  ];

//  d3.selectAll("input").on("change", selectDataset);

//  function selectDataset()
//  {
//      var value = this.value;
//      if (value == "total")
//      {
//          change(datasetTotal);
//      }
//      else if (value == "option1")
//      {
//          change(datasetOption1);
//      }
//      else if (value == "option2")
//      {
//          change(datasetOption2);
//      }
//  }

// var margin3 = {top: 20, right: 20, bottom: 30, left: 50},
//    width3 = 500 - margin3.left - margin3.right,
//    height3 =300 - margin3.top - margin3.bottom;

//  var div = d3.select("body").append("div").attr("class", "toolTip");

//  var formatPercent = d3.format("");

//  var y3 = d3.scale.ordinal()
//          .rangeRoundBands([height3, 0], .2, 0.5);

//  var x3 = d3.scale.linear()
//          .range([0, width3]);

//  var xAxis3 = d3.svg.axis()
//          .scale(x3)
//          .tickSize(-height3)
//          .orient("bottom");

//  var yAxis3 = d3.svg.axis()
//          .scale(y3)
//          .orient("left");
//  //.tickFormat(formatPercent);

//  var svg3 = d3.select("#graph3").append("svg")
//          .attr("width", width3 + margin3.left + margin3.right)
//          .attr("height", height3 + margin3.top + margin3.bottom)
//          .append("g")
//          .attr("transform", "translate(" + margin3.left + "," + margin3.top + ")");

//  svg3.append("g")
//          .attr("class", "x axis")
//          .attr("transform", "translate(0," + height3 + ")")
//          .call(xAxis3);

//  d3.select("input[value=\"total\"]").property("checked", true);
//  change(datasetTotal);

//  function change(dataset) {

//      y3.domain(dataset.map(function(d) { return d.age; }));
//      x3.domain([0, 490]);
//      // x3.domain([0, d3.max(dataset, function(d) { return d.friends; })]);

//      svg3.append("g")
//              .attr("class", "x axis")
//              .attr("transform", "translate(0," + height3 + ")")
//              .call(xAxis3);

//      svg3.select(".y.axis").remove();
//      svg3.select(".x.axis").remove();

//      svg3.append("g")
//              .attr("class", "y axis")
//              .call(yAxis3)
//              .append("text")
//              .attr("transform", "rotate(0)")
//              .attr("x", 30)
//              .attr("dx", ".1em")
//              .style("text-anchor", "end")
//              .text("Age");


//      var bar = svg3.selectAll(".bar")
//              .data(dataset, function(d) { return d.age; });
//      // new data:
//      bar.enter().append("rect")
//              .attr("class", "bar")
//              .attr("x", function(d) { return x3(d.friends); })
//              .attr("y", function(d) { return y3(d.age); })
//              .attr("width", function(d) { return width3-x3(d.friends); })
//              .attr("height", y3.rangeBand());

//      bar
//              .on("mousemove", function(d){
//                  div.style("left", d3.event.pageX+10+"px");
//                  div.style("top", d3.event.pageY-25+"px");
//                  div.style("display", "inline-block");
//                  div.html((d.age)+"<br>"+(d.friends)+" Friends");
//              });
//      bar
//              .on("mouseout", function(d){
//                  div.style("display", "none");
//              });


//      // removed data:
//      bar.exit().remove();

//      // updated data:
//      bar.transition()
//              .duration(750)
//              .attr("x", function(d) { return 0; })
//              .attr("y", function(d) { return y3(d.age); })
//              .attr("width", function(d) { return x3(d.friends); })
//              .attr("height", y3.rangeBand());

//  };

</script>

</div>
<div class="row">
<div id="footer col-xs-12 col-sm-6 offset-sm-2">
<h4 style="color:#8585ad">Please wait while we generate your visualization. </h4>
    <p></p>
<button id="Viz Button" type="submit" disabled>Visualization</button>
</div>
<script>
function getParamByName(name){
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
    results = regex.exec(window.location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

var uid  = getParamByName("user");
console.log(uid);

$.post('backendInit.php', { A : uid},function(result){
    // console.log(result);
    var domain = "https://das-lab.org/";
    var userdbdata = $.parseJSON(result);
    if (userdbdata["json"]) {
        document.getElementById("Viz Button").disabled = false;
        document.getElementById("Viz Button").onclick = function(){
            window.top.location.href = domain + "fbprojectb/viz.php?resp=" + getParamByName('resp') + "&user=" + getParamByName('user');
        }
    }
});
    </script>
    </div>
    </div>
    
    </body>
