
function checkArrays(annotations) {

	var summed_array = []
	var curr_annot = annotations[0];
	for (var i = 0; i < curr_annot.length; i++) {
		summed_array.push(parseInt(curr_annot[i]));
	}
	if (annotations.length > 0) {
		for (var i = 1; i < annotations.length; i++) {
			curr_annot  = annotations[i];
			for (var j = 0; j < annotations[0].length; j++) {
				var curr_val = parseInt(curr_annot[j])
				summed_array[j] += curr_val;
			}
		}
	} 
	console.log(summed_array);
	var max = Math.max.apply(null, summed_array)
	for (var i = 0; i < summed_array.length; i++) {
	    /*
		var value = (summed_array[i]/max).toFixed(2);
		console.log("rgba(255, 255, 0, " + value.toString() + ")");
		$('#' + i).css("background-color", "rgba(255, 255, 0, " + value.toString() + ")");	
		*/
		var value = ((summed_array[i])/(max));
		console.log("rgba(255, " + (Math.round((1.0 - value) * 255)).toString() + ", 0, " + (value > 0  ? "0.5" : "0") + ")");
		$('#' + i).css("background-color", "rgba(255, " + (Math.round((1.0 - value) * 255)).toString() + ", 0, " + (value > 0  ? "0.5" : "0") + ")");	
	}
		
}

function checkNone() {
	$('.passage_words').css("background-color", "rgba(255, 255, 0, 0)");
}



$(document).ready(function(){
	console.log(ator_ations);
	$('#checkall:input[type=checkbox]').on("click", function(e){ // the "check all" box is checked
		if ($('input[name="checkall"]:checked').length == 1) {
			var annotations = [];

			for (var i in ator_ations) {
				console.log(i);
				console.log(ator_ations[i]);
				annotations.push(ator_ations[i].split(' '));
			}
			checkArrays(annotations);
			$(".atorcheck").prop('checked', true);
		else { //nothing checked
			checkNone();
			$(".atorcheck").prop('checked', false);
		}
	});
	$( ".atorcheck:input[type=checkbox]" ).on( "click", function(e) {
		var annotations = [];
		if ($('input[name="checkall"]:checked').length == 1) {
			$('#checkall').prop('checked', false);
		}
		$("input:checked").each(function () {
			console.log($(this)[0].name);
			annotations.push(ator_ations[$(this)[0].name].split(' '))
		});
		if (annotations.length == 0) {
			checkNone();
		} else {
			checkArrays(annotations);
		}
	});

	$( "#checkcustom:input[type=checkbox]").on("click", function(e)){
		
	}
});
