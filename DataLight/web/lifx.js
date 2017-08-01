



var big5personalityMS;
var big5personalityYP;
var counter;
// lists all the light strips that are within range 
function lightShow()
{
    counter = 0;


    // somehow get lights 
    //f;or now use this thing
    big5personalityMS = [.43, .21, .95, .65, .43];
    big5personalityYP = [.76, .54, .21, .43, .81];

    // min and max values 
    for (var i = 0; i <= 4; i++)
    {
        if (big5personalityMS[i] < .2)
        {
            big5personalityMS[i] = .2;
        }
        if (big5personalityYP[i] < .2)
        {
            big5personalityYP[i] = .2;
        }


        if (big5personalityMS[i] > .8)
        {
            big5personalityMS[i] = .8;
        }
        if (big5personalityYP[i] > .8)
        {
            big5personalityYP[i] = .8;
        }
    }

    for (var i = 0; i <= 4; i++)
    {
        big5personalityMS[i] = (((big5personalityMS[i] - .2) / .6) * .5) + .5;
        big5personalityYP[i] = (((big5personalityYP[i] - .2) / .6) * .5) + .5;
    }

    clearLightsL();



    $.ajax({
        url: "https://api.lifx.com/v1/lights/label:Strip00/state",
        type: "put",
        headers:
                {
                    Authorization: "Bearer c54a000420aa2543b2abd0ea5f7a65d7bfc51a8a3b275013da646043c1fa5192"
                },
        dataType: 'json',
        data: {"power": "on", "color": "blue", "brightness": big5personalityMS[0], "duration": "5.0"},
        success: openRight,
        error: function (req, status, err) {
            console.log('something went wrong', status, err);
        }

    });

}



function clearLightsL()
{

    $.ajax({
        url: "https://api.lifx.com/v1/lights/label:Strip01/state",
        type: "put",
        headers:
                {
                    Authorization: "Bearer c54a000420aa2543b2abd0ea5f7a65d7bfc51a8a3b275013da646043c1fa5192"
                },
        dataType: 'json',
        data: {"power": "off"},
        success: clearLightsR,
        error: function (req, status, err) {
            console.log('something went wrong', status, err);
        }
    });
}

function clearLightsR()
{

    $.ajax({
        url: "https://api.lifx.com/v1/lights/label:Strip00/state",
        type: "put",
        headers:
                {
                    Authorization: "Bearer c54a000420aa2543b2abd0ea5f7a65d7bfc51a8a3b275013da646043c1fa5192"
                },
        dataType: 'json',
        data: {"power": "off"},
        success:
                {
                    //  
                },
        error: function (req, status, err) {
            console.log('something went wrong', status, err);
        }
    });

}







function wait()
{
    if (counter === 0)
    {
        setTimeout(fadeL, 10000);
        
    } else if (counter === 1)
    {
        setTimeout(fadeL, 10000);
    } else if (counter === 2)
    {
        setTimeout(fadeL, 10000);

    } else if (counter === 3)
    {
        setTimeout(fadeL, 10000);
    }
    
}


function fadeL()
{
    $.ajax({
        url: "https://api.lifx.com/v1/lights/label:Strip00/state",
        type: "put",
        headers:
                {
                    Authorization: "Bearer c54a000420aa2543b2abd0ea5f7a65d7bfc51a8a3b275013da646043c1fa5192"
                },
        dataType: 'json',
        data: {"power": "on", "duration": "7.0", "brightness": ".1"},
        success: fadeR,
        error: function (req, status, err) {
            console.log('something went wrong', status, err);
        }
    });
}

function fadeR()
{

    $.ajax({
        url: "https://api.lifx.com/v1/lights/label:Strip01/state",
        type: "put",
        headers:
                {
                    Authorization: "Bearer c54a000420aa2543b2abd0ea5f7a65d7bfc51a8a3b275013da646043c1fa5192"
                },
        dataType: 'json',
        data: {"power": "on", "duration": "5.0", "brightness": ".1"},
        success: fadeD,
        error: function (req, status, err) {
            console.log('something went wrong', status, err);
        }
    });

}


function fadeD()
{
    if (counter === 0)
    {
        counter++;
        setTimeout(conLeft, 3000);
    } 
    else if (counter === 1)
    {
        counter++;
        setTimeout(extraLeft, 3000);
    } 
    else if (counter === 2)
    {   counter++;   
        setTimeout(agreeLeft, 3000);
    }
    else if (counter === 3)
    {
        console.log(counter);
        counter++;
        setTimeout(neuroLeft, 3000);
    }
}






function openLeft()
{
    $.ajax({
        url: "https://api.lifx.com/v1/lights/label:Strip00/state",
        type: "put",
        headers:
                {
                    Authorization: "Bearer c54a000420aa2543b2abd0ea5f7a65d7bfc51a8a3b275013da646043c1fa5192"
                },
        dataType: 'json',
        data: {"power": "on", "color": "cyan", "brightness": big5personalityMS[0], "duration": "5.0"},
        success: wait,
        error: function (req, status, err) {
            console.log('something went wrong', status, err);
        }
    });
}

function openRight()
{
    $.ajax({
        url: "https://api.lifx.com/v1/lights/label:Strip01/state",
        type: "put",
        headers:
                {
                    Authorization: "Bearer c54a000420aa2543b2abd0ea5f7a65d7bfc51a8a3b275013da646043c1fa5192"
                },
        dataType: 'json',
        data: {"power": "on", "color": "cyan", "brightness": big5personalityYP[0], "duration": "5.0"},

        success: openLeft,
        error: function (req, status, err) {
            console.log('something went wrong', status, err);
        }

    });


}


function conLeft()
{
    $.ajax({
        url: "https://api.lifx.com/v1/lights/label:Strip00/state",
        type: "put",
        headers:
                {
                    Authorization: "Bearer c54a000420aa2543b2abd0ea5f7a65d7bfc51a8a3b275013da646043c1fa5192"
                },
        dataType: 'json',
        data: {"power": "on", "color": "purple", "brightness": big5personalityMS[1], "duration": "5.0"},
        success: conRight,
        error: function (req, status, err) {
            console.log('something went wrong', status, err);
        }

    });
}

function conRight()
{

    $.ajax({
        url: "https://api.lifx.com/v1/lights/label:Strip01/state",
        type: "put",
        headers:
                {
                    Authorization: "Bearer c54a000420aa2543b2abd0ea5f7a65d7bfc51a8a3b275013da646043c1fa5192"
                },
        dataType: 'json',
        data: {"power": "on", "color": "purple", "brightness": big5personalityYP[1], "duration": "5.0"},

        success: wait,
        error: function (req, status, err) {
            console.log('something went wrong', status, err);
        }

    });


}


function extraLeft()
{
    $.ajax({
        url: "https://api.lifx.com/v1/lights/label:Strip00/state",
        type: "put",
        headers:
                {
                    Authorization: "Bearer c54a000420aa2543b2abd0ea5f7a65d7bfc51a8a3b275013da646043c1fa5192"
                },
        dataType: 'json',
        data: {"power": "on", "color": "red", "brightness": big5personalityMS[2], "duration": "5.0"},
        success: extraRight,
        error: function (req, status, err) {
            console.log('something went wrong', status, err);
        }

    });
}

function extraRight()
{

    $.ajax({
        url: "https://api.lifx.com/v1/lights/label:Strip01/state",
        type: "put",
        headers:
                {
                    Authorization: "Bearer c54a000420aa2543b2abd0ea5f7a65d7bfc51a8a3b275013da646043c1fa5192"
                },
        dataType: 'json',
        data: {"power": "on", "color": "red", "brightness": big5personalityYP[2], "duration": "5.0"},

        success: wait,
        error: function (req, status, err) {
            console.log('something went wrong', status, err);
        }

    });


}




function agreeLeft()
{
    $.ajax({
        url: "https://api.lifx.com/v1/lights/label:Strip00/state",
        type: "put",
        headers:
                {
                    Authorization: "Bearer c54a000420aa2543b2abd0ea5f7a65d7bfc51a8a3b275013da646043c1fa5192"
                },
        dataType: 'json',
        data: {"power": "on", "color": "orange", "brightness": big5personalityMS[3], "duration": "5.0"},
        success: agreeRight,
        error: function (req, status, err) {
            console.log('something went wrong', status, err);
        }

    });
}

function agreeRight()
{
    $.ajax({
        url: "https://api.lifx.com/v1/lights/label:Strip01/state",
        type: "put",
        headers:
                {
                    Authorization: "Bearer c54a000420aa2543b2abd0ea5f7a65d7bfc51a8a3b275013da646043c1fa5192"
                },
        dataType: 'json',
        data: {"power": "on", "color": "orange", "brightness": big5personalityYP[3], "duration": "5.0"},

        success: wait,
        error: function (req, status, err) {
            console.log('something went wrong', status, err);
        }
    });
}



function neuroLeft()
{
    
    console.log("Guess it got here");
    $.ajax({
        url: "https://api.lifx.com/v1/lights/label:Strip00/state",
        type: "put",
        headers:
                {
                    Authorization: "Bearer c54a000420aa2543b2abd0ea5f7a65d7bfc51a8a3b275013da646043c1fa5192"
                },
        dataType: 'json',
        data: {"power": "on", "color": "green", "brightness": big5personalityMS[4], "duration": "5.0"},
        success: neuroRight,
        error: function (req, status, err) {
            console.log('something went wrong', status, err);
        }

    });
}

function neuroRight()
{

    $.ajax({
        url: "https://api.lifx.com/v1/lights/label:Strip01/state",
        type: "put",
        headers:
                {
                    Authorization: "Bearer c54a000420aa2543b2abd0ea5f7a65d7bfc51a8a3b275013da646043c1fa5192"
                },
        dataType: 'json',
        data: {"power": "on", "color": "green", "brightness": big5personalityYP[4], "duration": "5.0"},

        success: a,
        error: function (req, status, err) {
            console.log('something went wrong', status, err);
        }

    });
    
    function a() 
    {
        setTimeout(clearLightsL, 10000);
    }


}

