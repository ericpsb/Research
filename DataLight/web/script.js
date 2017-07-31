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
        addSliderBars();
        changeRangeColor();
    });
			
// embeded in submit button, load facebook and twitter login page
function loadLoginPage() {
        window.location='https://das-lab.org/datalight/login.html';
}

// fill up slider bars when moved 
function changeRangeColor() {
        $('input[type="range"]').mousemove(function() {
            var val = ($(this).val() - $(this).attr('min')) / ($(this).attr('max') - $(this).attr('min'));
            $(this).css('background-image',
                '-webkit-gradient(linear, left top, right top, '
                + 'color-stop(' + val + ', #62C462), '
                + 'color-stop(' + val + ', #DDE6D6)'
                + ')'
                );
        });
}

  // This is called with the results from from FB.getLoginStatus().
function statusChangeCallback(response) {
	console.log('statusChangeCallback');
	console.log(response);
    if (response.status === 'connected') {
      	getInfoAPI(getLikesPostsAPI);
    } else {
      // The person is not logged into your app or we are unable to tell.
      //	document.getElementById('status').innerHTML = 'Please log ' +
       // 'into this app.';
    }
}


function collectValues() {
    var values = [];
    for (i = 0; i < 10; i++) {
        var s = '#range-slider-' + i;
        values.push($(s).val());
    }
    disableSliderBars();
    sendQuiz(values);
} 


function disableSliderBars() {
/*
    for (i = 0; i < 10; i++) {
        var s = '#range-slider-' + i;
        $(s).prop('disabled', true);
        $(s).css('cursor', 'not-allowed');
    }
*/
    //$("#submit").prop('disabled', true);
    $('input[type="range"]').css('background', '#EEEEEE');
}

// add 10 slider bars to UI
function addSliderBars() {
    const keywords = ['Extraverted, enthusiastic', 'Critical, quarrelsome', 'Dependable, self-disciplined', 'Anxious, easily upset',
                      'Open to new experiences, complex', 'Reserved, quiet', 'Sympathetic, warm', 'Disorganized, careless', 
                      'Calm, emotionally stable', 'Conventional, uncreative'];

    for (i = 0; i < keywords.length; i++) {
        const s = 
                '<div class="range-slider">' +
                    '<input id="range-slider-' + i + '"' + 'type="range" value="0" min="0" max="100"/>' +
                    '<span class="range-slider-label">' + keywords[i] + '</span>' +
                '</div>' 
        $('#quiz').append(s);
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
	    const userId = response.id;
        console.log('Successful login for: ' + response.name);
        //document.getElementById('status').innerHTML =
        //'Thanks for logging in, ' + response.name + '!';
        getLikesPostsAPI(userId);
    });
    
}

function print() {
    console.log('get all likes successful');
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
        $.getJSON(nextPage, function(response) {
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
    }); 

    FB.api('/'+userId+'/posts?limit=100', 'get', function(response) {
        getAllPosts(response);
    });

}

function logout() {
    console.log('printing test');
	FB.logout(function(response) {
		console.log("You successfully logout");
		checkLoginState();
	});
}


// send all likes and get back an array of like predictions
function sendAllLikes() {
    $.ajax(
        '/likes',
        {
            type: 'POST',
            data: JSON.stringify({
                allLikes: allLikes 
            }),                 
            processData: 'true',
            contentType: 'application/json',
            dataType: 'json',
            success: function (result) {
                // printing out likes predictions
                console.log(result);
            }
        });
}

// send all posts and get back an array of post predictions
function sendAllPosts() {
    $.ajax(
        '/posts',
        {
            type: 'POST',
            data: JSON.stringify({
                allPosts: allPosts
            }),
            processData: 'true',
            contentType: 'application/json',
            dataType: 'json',
            success: function(result) {
                // printing out posts predictions
                console.log(result);
            }   
        });
}

function msPredictions() {
    $.ajax(
        '/mspredictions',
        {
            type: 'GET',
            processData: 'true',
            contentType: 'application/json',
            dataType: 'json',
            success: function(result) {
                console.log(result);
            }
        });
}

function sendQuiz(quizzes) {
    $.ajax(
        '/quizzes',
        {
            type: 'POST',
            data: JSON.stringify({
               quizzes: quizzes 
            }),
            processData: 'true',
            contentType: 'application/json',
            dataType: 'json',
            success: function(result) {
                console.log(result);
            }
    });
}
        
function quizPrediction() {
    $.ajax(
        '/quizzes',
        {
            type: 'GET',
            processData: 'true',
            contentType: 'application/json',
            dataType: 'json',
            success: function(result) {
                console.log('print quiz prediction');
                console.log(result);
            }
        });
}
