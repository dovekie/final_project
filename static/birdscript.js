// Manage the display of the user's bird data
jQuery.fn.extend({
    toggleText: function (a, b){
        var that = this;
            if (that.text() != a && that.text() != b){
                that.text(a);
            }
            else
            if (that.text() == a){
                that.text(b);
            }
            else
            if (that.text() == b){
                that.text(a);
            }
        return this;
    }
});

// When a logged-in user visits the homepage
// mark all the birds in their life list
$( document ).ready(function() {
    console.log( "Old bird marker is ready!" );
    $.get("/mark_user_birds", function (obs_list) {
		for (var property in obs_list) {
			$( "span#" + property ).addClass( "highlight" );
			$( "button#" + property ).toggleClass('add-bird');
			$( "button#" + property ).toggleClass('remove-bird');
			$( "button#" + property ).toggleText('Add This Bird', 'Remove This Bird');
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
	$( "span.species_span" ).click(function() {
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

$( document ).ready( function() {
	$( "button.add-bird" ).click( function() {
		console.log("add bird button id: " + $(this).attr("id"));
		if ($(this).hasClass('add-bird')) {
			$("#tweet-" + $(this).attr("id")).attr('href', "https://twitter.com/intent/tweet?text=Hey%20everyone!%20I%20saw%20a%20{{birds_nest[order][family][bird]['common_name']}}");
			$("#tweet-" + $(this).attr("id")).addClass('btn-primary');
		} else {
			$("#tweet-" + $(this).attr("id")).attr('href', "");
			$("#tweet-" + $(this).attr("id")).removeClass('btn-primary');
		}
	    $.ajax("/add_obs", {
	    	method: "POST",
	        datatype:"json",
	    	data: {'count': $("#bird_counter").html(), 'bird': $(this).attr("id")} 	// Nothing uses 'count'. Yet.
	    	}).done(function() {
					console.log("Victory! Database contacted successfully");  		// confirm in the console
			});
		$(".species_span#" + $(this).attr("id")).toggleClass("highlight");

		$(this).toggleClass('add-bird');
		$(this).toggleClass('remove-bird');
		$(this).toggleText('Add This Bird', 'Remove This Bird');

		console.log($(this).hasClass('add-bird'));
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

var bird_id;

$( document ).ready( function() {
	$(".delete_save_search").click( function() {
		$.ajax("/delete_search", {
		    	method: "POST",
		    	data: {'search_string': $(this).closest('div').children('form').serialize()}
		    }).done( function() {
		    	console.log("Victory!");
		    });
	});

});

var picture_html
$( document ).ready( function() {
	$(".bird_picture").each( function( index_number, this_item) {
			$.get('/bird_pictures', {'bird_id': $(this).attr('id')}, function(response) {
				bird_gallery_data = JSON.parse(response);
				console.log(bird_gallery_data);
				$("#" + bird_gallery_data.id).append(bird_gallery_data.uri);
			});
		});

});		


$( document ).ready( function () {
	$( ".species_info" ).click( function( evt ) {

		console.log( "Species info! " + evt );
		console.log( $( this ).parent( 'div' ).children( '.species_span' ).attr( 'id' ));

		var modal_id = $( this ).parent( 'div' ).children( '.species_span' ).attr( 'id' ) + "_modal";
		$("#"+modal_id+"_body").html('');


			$.get('/bird_pictures', {'bird_id': $(this).parent('div').children('.species_span').attr('id')}, function(response) {
				bird_gallery_data = JSON.parse(response);

				console.log(bird_gallery_data);

				$("#"+modal_id+"_body").append(bird_gallery_data.uri);
			});
		$( "#"+modal_id ).modal();
	});
});


// make a google map

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