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
        // make `Make a Prediction from Facebook` button disabled until login with facebook
        $('#predict-facebook').prop('disabled', true);
        $('#next-lightshow').prop('disabled', true);
        //animateProgressBar();
    });
			
// enable `Next` button after `Make Prediction from Facebook` clicked 
function enableNext() {
    $('#next-lightshow').prop('disabled', false);
    $('#status').text('Your prediction is complete. Click "Next" to see the light show');
}

// embeded in `submit` button, load facebook and twitter login page
function loadLoginPage() {
        window.location='/login.html';
}

// when the light show starts, this brings up the legend
function loadLegendPage() {
        window.location='./legend.html';
}

function toggleLegend() {
    var x = document.getElementById('legend');
    if (x.style.display === 'none') {
        x.style.display = 'block';
    } else {
        x.style.display = 'none';
    }
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
	//console.log('statusChangeCallback');
	console.log(response);
    if (response.status === 'connected') {
      	getInfoAPI(getLikesPostsAPI);
        $('#predict-facebook').prop('disabled', false);
    } else {
        $('#status').text('Please login using your social media account');
/*
        The person is not logged into your app or we are unable to tell.
        document.getElementById('status').innerHTML = 'Please log ' +
        'into this app.';
        $('#status').text('Please log in using Facebook');
*/
    }
}

function animateProgressBar(callback) {
    $('.progress-bar').animate({
        width: '100%'
    }, 5000, function() {
        callback();
    }); 
    var htmlString = "Fetching your information...";
    $('#status').text(htmlString);
}

function collectValues() {
    console.log('this is in collectvalues in script.js');
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
                    '<div class="range-slider-label">' + keywords[i] + '</div>' +
                    '<input id="range-slider-' + i + '"' + 'type="range" value="0" min="0" max="100"/>' +
                    '<div id="min">Strongly Disagree</div>' + 
                    '<div id="max">Strongly Agree</div>' +
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
    //console.log('Welcome!  Fetching your information.... ');
    FB.api('/me', 'get', function(response) {
	    const userId = response.id;
        //console.log('Successful login for: ' + response.name);
        var htmlString = 'Welcome! ' + response.name + ' You successfully login.';
        $('#status').text(htmlString); 
        //document.getElementById('status').innerHTML =
        //'Thanks for logging in, ' + response.name + '!';
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
        '/backend/likes',
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
        '/backend/posts',
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
        '/backend/mspredictions',
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
        '/backend/quizzes',
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
        '/backend/quizzes',
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

function print() {
    console.log('next button clicked');
}

function sendMail() {
    var email = $('#e-mail').val();
    console.log('this email is' + email);
    $.ajax(
        '/backend/mail',
            {
                data: JSON.stringify({
                email: email 
            }),
            processData: 'true', 
            contentType: 'application/json',
            dataType: 'json',
            type: 'POST',
            success: function(result) {
                console.log('inside sendMail() on script.js');
                console.log(result);
            }
        });
}
