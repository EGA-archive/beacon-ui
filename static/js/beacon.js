(function(){ // scoping

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
