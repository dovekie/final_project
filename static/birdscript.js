// Manage the display of the user's bird data


// When a logged-in user visits the homepage
// mark all the birds in their life list
$( document ).ready(function() {
    console.log( "Old bird marker is ready!" );
    $.get("/mark_user_birds", function (obs_list) {
		for (var property in obs_list) {
			$( "#" + property ).addClass( "highlight" );
		}
	});
});

// When a logged-in user visits the homepage
// get the total number of birds in their life list
$( document ).ready( function() {
	console.log("Bird counter is ready!");
	$.get("/birdcount", function (birdcount) {
		console.log ("birdcount: " + birdcount);
		$("#bird_counter").html(birdcount);
	});
});

// When any user clicks on a bird's name
// Send that user's info and bird info to the database
$( document ).ready( function() {
	console.log("New bird marker is ready!")
	$( "p.species_span" ).click(function() {
	  $( this ).toggleClass("highlight");  				// mark the new bird

	  var birdcount_update = $("#bird_counter").html() // get the value that was placed inside the bird counter

	  if ( $( this ).is( ".highlight" ) ) { 			// if the user has clicked a new bird
	  	console.log("Adding a bird");
	  	birdcount_update++;								// increment the bird counter
	  	$("#bird_counter").html(birdcount_update);
	  	console.log("Increased count is now " + $("#bird_counter").html()); 		// and update the DOM
	  } else {											// conversely, if they are removing a bird
	  	console.log("Removing a bird");
	  	birdcount_update--;								// decrement the counter
	  	$("#bird_counter").html(birdcount_update); 
	  	console.log("Decreased count is now " + $("#bird_counter").html());		// and update the DOM
	  }

		// Send the new bird to the database
	    $.ajax("/add_obs", {
	    	method: "POST",
	        datatype:"json",
	    	data: {'count': $("#bird_counter").html(), 'bird': $(this).attr("id")} 	// Nothing uses 'count'. Yet.
	    	}).done(function() {
					console.log("Victory! Database contacted successfully");  		// confirm in the console
			});
	  });
});

// Save a user search

$("#isDefaultChecked").click( function () {
	$("#isSaveChecked").attr("checked", true);
});

$( document ).ready( function() {
	$( "form.form-search" ).submit( function() {

		if( document.getElementById('isSaveChecked').checked ) {
			console.log("save_this is checked.");
		    console.log( $( "form.form-search" ).serialize() );

			    $.ajax("/add_search", {
			    	method: "POST",
			    	data: {'search_string': $( "form.form-search" ).serialize()}
			    }).done( function() {
			    	console.log("Victory!");
			    });
		} else {
		    console.log("not saved");
		}



		if( document.getElementById('isDefaultChecked').checked ) {
		    console.log( "A new default!" );

			    $.ajax("/change_default", {
			    	method: "POST",
			    	data: {'search_string': $( "form.form-search" ).serialize()}
			    }).done( function() {
			    	console.log("Victory!");
			    });
		} else {
		    console.log("not default");
		}
	});
});

$( document ).ready( function() {
	// on click, run the change_default route
	$(".default_set_button").click( function() {
		console.log($(this).closest('div').children('form').serialize()); // this produces the same string as form.form-search.serialize above
		    $.ajax("/change_default", {
		    	method: "POST",
		    	data: {'search_string': $(this).closest('div').children('form').serialize()}
		    }).done( function() {
		    	console.log("Victory!");
		    });
	});
});

$( document ).ready( function() {
	$(".delete_save_search").click( function() {
		console.log("deleting! jk not really");
	});

});
// omg map

// var map;

// function initialize() {

//     var mapOptions = {
//       zoom: 8,
//       center: {lat: -34.397, lng: 150.644}
//     };

//     map = new google.maps.Map(
//         document.getElementById('map-canvas'),
//         mapOptions);

// }

// google.maps.event.addDomListener(window, 'load', initialize);