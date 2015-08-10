//speaker-to-internets



$( document ).ready(function() {
	var happycount = 0;
    console.log( "ready!" );
    $.get("/mark_user_birds", function (obs_list) {
		console.log(obs_list);
		for (var property in obs_list) {
			console.log("property " + property);
			$( "#" + property ).addClass( "highlight" );
			birdcount = $('.highlight').length;
			$("#bird_counter").html(birdcount);
			}
		}
	);
});


$( document ).ready( function() {
	// $.get("/birdcount", function (birdcount) {
	// 	console.log ("birdcount: " + birdcount);
	// 	$("#bird_counter").html(birdcount);
	// })
	$( "p.species_span" ).click(function() {
	  $( this ).toggleClass("highlight");
	  if ( $( this ).is( ".highlight" ) ) {
	  	// happycount++;
	   //  console.log("happy = " + happycount);
		} else {
		// happycount--;
	 //    console.log("happy = " + happycount);
		}

		birdcount = $('.highlight').length;
		$("#bird_counter").html(birdcount);

	    $.ajax("/add_obs", {
	    	method: "POST",
            datatype:"json",
	    	data: {'count': birdcount, 'bird': $(this).attr("id")}
	    }).done(function() {
  			console.log("Victory!");
		});
	  });
	})