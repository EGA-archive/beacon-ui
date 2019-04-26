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
    $( ".trigger" ).click(function() {
	$( this ).parent('div').toggleClass( "open" );
    });



    var filters = $( "#query-filters" );
    filters.delegate( ".filter-add", "click", function() {

	var tpl = '<section>' + 
	          '  <input type="text" value="" placeholder="HP:0011007>=49 or PATO:0000383 or EFO:0009656" name="filters" data-lpignore="true" />' + 
	          '  <i class="filter-remove fas fa-minus-circle"></i>' +
	          '</section>';

	var me = $(tpl);
	filters.append(me);
    });

    filters.delegate( ".filter-remove", "click", function() {
	$( this ).parent('section').remove();
    });

})();
