// USE TO CLEAR CHROME STORAGE
// chrome.storage.sync.clear();
// Saves options to chrome.storage
function save_options() {
    var actKey = document.getElementById('actKey').value;
    var determinant = 0;

    $.ajax({
        dataType: 'text',
        type: "POST",
        url: "http://junghosohn.com/verify.php",
        data: {
            actKey: actKey
        },
        crossDomain: true,
        success: function (result) {
            // do stuff with json (in this case an array)
            determinant = result;
            if (determinant == 1) {

                chrome.storage.sync.set({
                    activationKey: actKey
                }, function () {
                    alert("Activation Key Saved.");
                });
            } else {
                alert("Incorrect Activation Key.");
            }
        },
        error: function () {
            alert("Failed to Access Server, Please Contact Us.");
        }
    });


    // $.ajax({url:"demo_test.txt",success:function(result){
    //       $("#div1").html(result);
    //     }});

}


var masterWhiteList = new Array();
// Saves options to chrome.storage
function add_options() {
    if (document.getElementById('whitelist').value != "") {
        var whitelist = document.getElementById('whitelist').value;
        // masterWhiteList.push(whitelist);

        var add = 0;

        for (q = 0; q < masterWhiteList.length; q++) {
            if (masterWhiteList[q] != whitelist.replace('http://', '').replace('https://', '').replace('http://www.', '').replace('https://www.', '').replace('www.', '').split(/[/?#]/)[0]) {
                add = 1;
                continue;
            } else {
                add = 0;
                alert(whitelist + " is already on the list.")
                break;
            }
        }
        if (add == 1) {
            masterWhiteList.push(whitelist.replace('http://', '').replace('https://', '').replace('http://www.', '').replace('https://www.', '').replace('www.', '').split(/[/?#]/)[0]);

        }
    }

    chrome.storage.sync.set({
        masterWhiteList: masterWhiteList
    }, function () {
        if (add == 1) {
            alert(whitelist + " has been added to the list.");
            location.reload();
        }
    });
}


// alert(masterWhiteList);
// for(i=0, i<masterWhiteList.length, i++){
//   sitelist.textContent = masterWhiteList[0];
// }

// Restores select box and checkbox state using the preferences
// stored in chrome.storage.
function restore_options(callback) {
    // Use default value color = 'red' and likesColor = true.
    chrome.storage.sync.get({
        activationKey: "",
        whitelist: "",
        masterWhiteList: ""
    }, function (items) {
        var actKey = items.activationKey;
        document.getElementById('actKey').value = items.activationKey;
        var masterWhiteList1 = items.masterWhiteList;



        var adder = 0;

        for (n = 0; n < masterWhiteList1.length; n++) {
            // for(l=0; l<masterWhiteList.length; l++){
            // if(masterWhiteList1[n]==masterWhiteList[l]){
            // break;
            // }
            // else {
            // if(l+1==masterWhiteList.length){
            masterWhiteList.push(masterWhiteList1[n]);
            // }

            // }
            // }
        }
        callback(masterWhiteList);
    });
}
document.addEventListener('DOMContentLoaded', restore_options(printList));

document.getElementById('save').addEventListener('click', save_options);

document.getElementById('add').addEventListener('click', add_options);


// if(masterWhiteList==""||masterWhiteList==undefined){
// var masterWhiteList = ["nytimes.com", "derger.com"];
// }



function printList() {
    // console.log(masterWhiteList);
    if (masterWhiteList.length < 1) {
        masterWhiteList = ["foxnews.com","npr.org","washingtonpost.com","latimes.com", "abcnews.go.com", "cnn.com", "theguardian.com", "economist.com", "bbc.com", "huffingtonpost.com", "reuters.com"];
    }
    for (i = 0; i < masterWhiteList.length; i++) {
        var divbox = document.createElement("div");
        divbox.setAttribute("class", "sitelist");
        var button = document.createElement("input");
        button.setAttribute("type", "radio");
        button.setAttribute("name", "delete");
        button.setAttribute("id", i);
        // button.setAttribute("onclick","deleteFunction("+i+");");
        // document.getElementsByTagName('body')[0].appendChild(button);
        var para = document.createElement("p");
        para.appendChild(document.createTextNode(masterWhiteList[i]));
        // document.getElementsByTagName('body')[0].appendChild(para); 
        divbox.appendChild(button);
        divbox.appendChild(para);
        document.getElementById('list').appendChild(divbox);
    }
}



// function activationFunction(){
//     activationKey = activation;
//     if (activation!=undefined&&activation!="") {
//         for(mwlCnt=0; mwlCnt<masterWhiteList.length; mwlCnt++){


//             sourceUrl = sourceUrl.replace('www.','');

//             var masterUrl = masterWhiteList[mwlCnt].replace('http://','').replace('https://','').replace('http://www.','').replace('https://www.','').replace('www.','').split(/[/?#]/)[0];
//             console.log(masterUrl);
//             if(sourceUrl == masterUrl){

//                 break;
//             }
//             if(mwlCnt+1 == masterWhiteList.length){
//                 if(sourceUrl != masterUrl) {
//                     return false;
//                 }
//             }
//         }




chrome.runtime.onMessage.addListener(function (request, sender, sendResponse) {
    if (request.method == "getStatus")
        sendResponse({
            status: syncStorage['status']
        });
    else
        sendResponse({});
});




function delete_options() {
    console.log("dpf");
    var chk = $("input[name=delete]:checked").attr('id');

    console.log(chk);


    if (chk > -1) {
        masterWhiteList.splice(chk, 1);
    }
    // alert(masterWhiteList);



    chrome.storage.sync.set({
        // whitelist: whitelist,
        masterWhiteList: masterWhiteList
    }, function () {
        // Update status to let user know options were saved.


        location.reload();
    });
}

document.getElementById('delete').addEventListener('click', delete_options);