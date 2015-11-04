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

// Go through a pre-sorted list of orders
// Find orders that are in the current search results
// and push divs for those orders to the homepage.
function makeOrderDivs() {
	for (var i = 0; i < sp_orders.length; i++) {
		if (sp_orders[i] in birds_nest && $('#' + sp_orders[i]).length===0){
			var orderDiv = $('<div></div>');
			orderDiv.attr('id', sp_orders[i]);
			orderDiv.addClass('taxon_order');
			orderDiv.text(sp_orders[i]);
			$("#bird-list").append(orderDiv);
		}
	}
}

// create all family divs on the homepage
function makeFamilyDivs(order) {
	var families = birds_nest[order];
	for( var family in families ) {
		if ($('#' + family).length === 0){
			var familyDiv = $('<div></div>');
			familyDiv.attr('id', family);
			familyDiv.addClass('taxon_family');
			familyDiv.text(family);
			$("#" + order).append(familyDiv);
		}
	}
}

// Create all species divs on the homepage
function makeSpeciesDivs() {

	for ( var taxonId in all_taxons ) {
		var birdObject = all_taxons[taxonId];
		var familyDiv = $('#' + birdObject.family);

		var speciesDiv = $('<div></div>');
		speciesDiv.addClass('taxon_species');

		var speciesSpan = $('<span></span>');
		speciesSpan.attr('id', taxonId);
		speciesSpan.addClass('species_span');
		speciesDiv.append(speciesSpan);

		var comNameSpan = $('<span></span>');
		comNameSpan.addClass("common_name_span");
		comNameSpan.text(birdObject.common_name + ": ");
		speciesSpan.append(comNameSpan);

		var sciNameSpan = $('<span></span>');
		sciNameSpan.addClass("sci_name_span");
		sciNameSpan.text(birdObject.sci_name);
		speciesSpan.append(sciNameSpan);

		var spInfo = $('<span></span>');
		spInfo.addClass("species_info");
		spInfo.insertAfter(speciesSpan);

		var infoGlyph = $('<span></span>');
		infoGlyph.addClass("glyphicon glyphicon-question-sign");
		infoGlyph.attr('aria-hidden', 'true');
		spInfo.append(infoGlyph);

		familyDiv.append(speciesDiv);
	}
}

// If a species-span does not have a modal window attached to it,
// this function will add one.
function addModal(taxonId) {
	if ($('#' + taxonId).next().attr("class") !== "modal fade") {
		var birdObject = all_taxons[taxonId];
		var modalHTML = '<div class="modal fade" id="' + taxonId + '_modal">' +
			'<div class="modal-dialog">' +
			'<div class="modal-content">' +
			'<div class="modal-header">' +
			'<button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>' +
			'<h4 class="modal-title"><span class="modal-common-name">' + birdObject.common_name + '</span></h4>' +
			'<div class="modal-bird-info"><span class="modal-sci-name sci_name_span">(' + birdObject.sci_name + ')</span>' +
			'<div class="modal-range">Region codes: ' + birdObject.region + '</div></div></div>' +
			'<div class="modal-body" id="' + taxonId + '_modal_body"></div>' + 
			'<div class="modal-footer"><button type="button" class="btn btn-default" data-dismiss="modal">Close Window</button>' +
			'<button type="button" class="btn btn-primary add-bird" id="' +
			taxonId + '" data-taxon-id="' + birdObject.common_name + '">Add This Bird</button>' + 
			'<a class="btn twitter-share-button" id="tweet-' + taxonId + '">Tweet This Bird</a></div>' + 
			'</div><!-- /.modal-content --></div><!-- /.modal-dialog --></div><!-- /.modal -->';

		$(modalHTML).insertAfter($('#' + taxonId));
	}
}

// When a logged-in user visits the homepage
// mark all the birds in their life list
function markOldBirds() {
	console.log( "Old bird marker is ready!" );
    $.get("/mark_user_birds", function (obs_list) {
		for (var property in obs_list) {
			$( "span#" + property ).addClass( "highlight" );
			$( "button#" + property ).toggleClass('add-bird');
			$( "button#" + property ).toggleClass('remove-bird');
			$( "button#" + property ).toggleText('Add This Bird', 'Remove This Bird');
		}
	});
}

// When a logged-in user visits the homepage
// get the total number of birds in their life list
function getBirdcount() {
	console.log("Bird counter is ready!");
	$.get("/birdcount", function (birdcount) {
		console.log ("birdcount: " + birdcount);
		$("#bird_counter").html(birdcount);
	});
}

// When any user clicks on a bird's name
// Send that user's info and bird info to the database
function markNewBird() {
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
}

function tweetBird() {
	$( "button.add-bird" ).click( function() {
		console.log("add bird button id: " + $(this).attr("id"));
		if ($(this).hasClass('add-bird')) {
			var comName = $(this).data("taxonId");
			$("#tweet-" + $(this).attr("id")).attr('href', "https://twitter.com/intent/tweet?text=Hey%20everyone!%20I%20saw%20a%20"+comName+"&via=LekLifeList");
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
}


// Save a user search
function saveSearch() {
	$("#isDefaultChecked").click( function () {
		$("#isSaveChecked").attr("checked", true);
	});

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
}

function changeDefaultSearch() {
	// on click, run the change_default route
	$(".default_set_button").click( function() {
		console.log($(this).parents('form').serialize());
		    $.ajax("/change_default", {
		    	method: "POST",
		    	data: {'search_string': $(this).parents('form').serialize()}
		    }).done( function() {
		    	console.log("Victory!");
		    });
	});
}

function deleteSavedSearch() {
	$(".delete_save_search").click( function() {
		$.ajax("/delete_search", {
	    	method: "POST",
	    	data: {'search_string': $(this).parents('form').serialize()}
	    }).done( function() {
		    location.reload(true);
	    	console.log("Victory!");
	    });
	});
}

function makeBirdGallery() {
	var bird_id;
	$(".bird_picture").each( function( index_number, this_item) {
			$.get('/bird_pictures', {'bird_id': $(this).attr('id')}, function(response) {
				var bird_gallery_data = JSON.parse(response);
				console.log(bird_gallery_data);
				if (bird_gallery_data.uri === "<span></span>") {
					console.log('No photo found');
				} else {
					var bird_id = "#" + bird_gallery_data.id;
					$(bird_id).children('a').replaceWith(bird_gallery_data.uri);
					// hands down the gnarliest piece of javascript I've ever written. For posterity.
					// $("#" + bird_gallery_data.id).children('div').children('h3').text($("#" + bird_gallery_data.id).children('a').attr('title'));
				}
			});
		});
}

// function birdScrolling() {
//     window.onscroll = function() {
//     	var scroll = $(this).scrollTop(); // Get the vertical scroll position
//     	var height = $("#bird-list").height(); // Get height of the bird list
//     	if( (height - scroll) < 1000) {
//     		loadMoreBirds();
//     	}
// 	}
// }

// function loadMoreBirds() {
// 	if (typeof scrollCounter === 'undefined') {
//     	var scrollCounter = 1;
// 	} else {
// 		scrollCounter += 1;
// 	}
// 	console.log("me go too far!");
// 	console.log("last div", $("#bird-list div:last"));
// 	var lastBird = $("#bird-list div:last").children("button:last")[0].id;
// 	var lastFamily = all_taxons[lastBird].family;
// 	var lastOrder = all_taxons[lastBird].order;
// 	console.log($("#" + lastFamily));
// 	console.log($("#" + lastOrder));

// 	function putBirdsOn(moreBirds) {
// 		sp_orders = moreBirds.orders;
// 		birds_nest = moreBirds.birds_nest;
// 		all_taxons = moreBirds.all_taxons;
// 		nextOrder = sp_orders.indexOf(lastOrder) + 1;
// 		makeOrderDivs();
// 		makeFamilyDivs();
// 		makeSpeciesDivs();
// 		$(".species_span").each( function(i){
// 			console.log("1! add modal", $(".species_span")[i].id)
// 			addModal($(".species_span")[i].id)
// 		});
// 	}

// 	function goGetBirds(putBirdsOn) {
// 			$.get('/more_birds', {'scroll_counter': scrollCounter}, function (response) {
// 			var gotBack = JSON.parse(response);
// 			putBirdsOn(gotBack);
// 		});
// 	}

// 	goGetBirds(putBirdsOn);

// 	// console.log(newAllTaxons[0]);

//     window.onscroll = function() {
//     	var scroll = $(this).scrollTop(); // Get the vertical scroll position
//     	var height = $("#bird-list").height(); // Get height of the bird list
//     	if( (height - scroll) > 1000) {
//     		birdScrolling();
//     	}
// 	}
// }



$( document ).ready( function () {
	// functions for the homepage
	if ("sp_orders" in window) {
		makeOrderDivs();
		$(".taxon_order").each( function(i){
			makeFamilyDivs($(".taxon_order")[i].id);
		});
		makeSpeciesDivs();
		$(".species_span").each( function(i){
			addModal($(".species_span")[i].id)
		});
		markNewBird();
		markOldBirds();
		tweetBird();
		// birdScrolling(); // Part of the infinite scroll system
	}
	// functions for all pages
	makeBirdGallery();
	deleteSavedSearch();
	saveSearch();
	changeDefaultSearch();
	getBirdcount();

	// event handler for modal windows
	$( ".species_info" ).click( function( evt ) {

		console.log( "Species info!");
		console.log( $( this ).closest( 'div' ));

		var modal_id = $( this ).closest( 'div' ).children( '.species_span' ).attr( 'id' ) + "_modal";
		$("#"+modal_id+"_body").html('');


			$.get('/bird_pictures', {'bird_id': $(this).closest('div').children('.species_span').attr('id')}, function(response) {
				bird_gallery_data = JSON.parse(response);

				console.log(bird_gallery_data);

				$("#"+modal_id+"_body").append(bird_gallery_data.uri);
			});
		$( "#"+modal_id ).modal();
	});

// Runs the simple search box on the homepage
	console.log($( "#simple-search" ).val());
	$( "#simple-search" ).keydown( function(evt) {
	    if (evt.keyCode == 13) {
	        evt.preventDefault();
			console.log($( "#simple-search" ).val());
			var thisSearch = $( "#simple-search" ).val()
			window.find(thisSearch);
	    }
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