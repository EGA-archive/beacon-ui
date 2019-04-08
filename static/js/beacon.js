(function(){ // scoping

    var cookiePane = document.querySelector('#beacon-cookies'),
	cookieButton = null;
    if(cookiePane)
	cookieButton = cookiePane.querySelector('button');
    if(cookiePane && cookieButton)
	cookieButton.addEventListener('click', function(){
	    document.cookie = "beacon=consent;path=/";
	    cookiePane.setAttribute("class", 'hide-me'); // set to 1s
	    setTimeout(function(){ cookiePane.remove(); }, 1100);
	    return false;
	});


    // Click/Toggle sidebar panel
    $( "form#query > span" ).click(function() {
	$( this ).parents('body').toggleClass( "open" );
    });
    
    
    var assemblyField = $( "#id_assemblyID" );
    $( "#id_datasets" ).on('change', function() {
	var a = $( this ).find("option:selected").attr('data-assemblyid');
	assemblyField.val(a);
    }).trigger('change');


    
})();
