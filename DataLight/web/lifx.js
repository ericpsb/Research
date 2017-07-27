
function listLights() {
    return $.ajax({
        url: "https://api.lifx.com/v1/lights/all",
        type: "get",
        headers: {
            Authorization: "Bearer c54a000420aa2543b2abd0ea5f7a65d7bfc51a8a3b275013da646043c1fa5192"
        },
        dataType: 'json',
        success: function(data, status){
            return alert("Data: " + data + "\nStatus: " + status);
        }
    });
}
