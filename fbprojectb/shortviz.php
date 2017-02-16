<?php 
	$ac = "EAAWfa2M5ZBkEBAJj4STWrWcK5C2DBQfu7PSjsbQZCTe2hgSgbn35RZBJFet0ZC7F7NHMv81xVVyV3dz8I0jr1EO6mLNw74PMd4yx7xWUt7JJzehTW8VYtcdULT6RPdFLyOgvP4KSU8HEZAtYa9Qt9wx7jiuA2x82yu4i1lnWkOgZDZD";

	#Birthday must be in mm/dd/yyyy format
	function getAge($birthday){
		$birthday = explode("/", $birthday);
		$age = (date("md", date("U", mktime(0, 0, 0, $birthday[0], $birthday[1], $birthday[2])))
			> date("md") ? ((date("Y") - $birthday[2]) - 1) : (date("Y") - $birthday[2]));
		return $age;
	};	

	function getUserData($accessToken){
		#Generating FB Graph API request urls
		$fb = "https://graph.facebook.com/v2.7/me?fields=";
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
		$client = new MongoClient("localhost:27017");
		$db = $client->selectDB("fb_nonuse_Nov_20");
		$collection = new MongoCollection($db, 'user');

		#Setting
		$query = array('total_friends' => array( '$exists' => true ));
        $fields = array('total_friends' => true, '_id' => false, 'birthday' => true, 'gender' => true);
        $cursor = $collection->find($query, $fields);
		$array = iterator_to_array($cursor);
		$array2 = [];
		foreach ($array as $key => $value) {
			$value["age"] = getAge($value["birthday"]);
			array_push($array2, $value);
			
		};

		return json_encode($array2);
	}

?>

<script>

var dbdata  = <?php echo getDBdata()?>;
var user = <?php echo getUserData($ac)?>;
console.log("aa");

var dbfriendarray = dbdata.map(function(d){
	return d.total_friends;
}).sort(function(a,b){
	return a-b;
});

console.log(dbfriendarray);

</script>