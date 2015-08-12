// Manage the display of the user's bird data


// When a logged-in user visits the homepage
// mark all the birds in their life list
$( document ).ready(function() {
    console.log( "ready!" );
    $.get("/mark_user_birds", function (obs_list) {
		console.log(obs_list);
		for (var property in obs_list) {
			$( "#" + property ).addClass( "highlight" );
		}
	});
});

// When a logged-in user visits the homepage
// get the total number of birds in their life list
$( document ).ready( function() {
	$.get("/birdcount", function (birdcount) {
		console.log ("birdcount: " + birdcount);
		$("#bird_counter").html(birdcount);
	});
});

// When any user clicks on a bird's name
// Send that user's info and bird info to the database
$( document ).ready( function() {
	$( "p.species_span" ).click(function() {
	  $( this ).toggleClass("highlight");  				// mark the new bird

	  var birdcount_update = $("#bird_counter").html() // get the value that was placed inside the bird counter

	  if ( $( this ).is( ".highlight" ) ) { 			// if the user has clicked a new bird
	  	console.log("Adding a bird");
	  	birdcount_update++;								// increment the bird counter
	  	$("#bird_counter").html(birdcount_update); 		// and update the DOM
	  } else {											// conversely, if they are removing a bird
	  	console.log("Removing a bird");
	  	birdcount_update--;								// decrement the counter
	  	$("#bird_counter").html(birdcount_update); 		// and update the DOM
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