//speaker-to-internets

var happycount = 0;

$( "p" ).click(function() {
	  $( this ).toggleClass("highlight");
	  if ( $( this ).is( ".highlight" ) ) {
	  	happycount++;
	    console.log("happy = " + happycount);
		} else {
		happycount--;
	    console.log("happy = " + happycount);
		}
	    $("#bird_counter").html(happycount);
	  });