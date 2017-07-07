$(document).ready(function() {
		$.ajaxSetup({ cache: true});
		$.getScript('//connect.facebook.net/en_US/sdk.js', function() {
  			FB.init({
    			appId      : '453093795064853',
    			cookie     : true,  // enable cookies to allow the server to access session
			    xfbml      : true,  // parse social plugins on this page
			    version    : 'v2.8' // use graph api version 2.8
			  });
		
            FB.getLoginStatus(function(response) {
            	statusChangeCallback(response);
            });
	    });
    });
			
  // This is called with the results from from FB.getLoginStatus().
function statusChangeCallback(response) {
	console.log('statusChangeCallback');
	console.log(response);
    if (response.status === 'connected') {
      	getInfoAPI(getLikesPostsAPI);
    } else {
      // The person is not logged into your app or we are unable to tell.
      	document.getElementById('status').innerHTML = 'Please log ' +
        'into this app.';
    }
}

function checkLoginState() {
	FB.getLoginStatus(function(response) {
	statusChangeCallback(response);
    });
}

function getInfoAPI(getLikesPostsAPI) {
    console.log('Welcome!  Fetching your information.... ');
    FB.api('/me', 'get', function(response) {
	    var userId = response.id;
        console.log('Successful login for: ' + response.name);
        document.getElementById('status').innerHTML =
        'Thanks for logging in, ' + response.name + '!';
        getLikesPostsAPI(userId);
    });
    
}

var allLikes = []; 
// retrieve all user's likes
function getAllLikes(response) {
    // likes is an arry of size 100 objects
    var likes = response.data;
    for (i in likes) {
        allLikes.push(likes[i].id);
    }
    
    try { 
        var nextPage = response.paging.next;
	//console.log('Printing before getJSON: ' + nextPage);
        $.getJSON(nextPage, function(response) {
			//console.log('Printing after getJSON: ' + nextPage);
             getAllLikes(response);
        });
    } catch (e) {
        console.log('exception thrown');
    }
}

var allPosts = [];
function getAllPosts(response) {
    // posts is an arry of size 100 objects
    var posts = response.data;
    for (i in posts) {
        if(posts[i].message) {  
            allPosts.push(posts[i].message);
        } 
    }
    try {    
        var nextPage = response.paging.next;
        $.getJSON(nextPage, function(response) {
			console.log('Posts Printing after getJSON: ' + nextPage);
            getAllPosts(response);
        });
    } catch (e) {
        if (e instanceof TypeError) {
            console.log('no more pages');
        }
    }
}

function getLikesPostsAPI(userId) {
    FB.api('/'+userId+'/likes?limit=100', 'get', function(response) {
        getAllLikes(response);
        console.log(allLikes);
    }); 

    FB.api('/'+userId+'/posts?limit=100', 'get', function(response) {
        getAllPosts(response);
        console.log(allPosts);
    });

}

function logout() {
    console.log('printing test');
	FB.logout(function(response) {
		console.log("You successfully logout");
		checkLoginState();
	});
}

/*function getToken() {
    $.ajax(
        '/token',
        {
            type: 'GET',
            processData: 'false',
            dataType: 'json',
            success: function (result) {
                console.log('token successful');
            }
        });
}*/
