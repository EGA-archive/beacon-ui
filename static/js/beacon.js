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

    var datasets = $( "#query-datasets" );
    var datasetsSelectors = datasets.find( "input:not([disabled])" ); // enough
    datasets.find("> p").delegate( "span", "click", function() {
	var content = $( this ).text();
	if( content == 'All' ){
	    datasetsSelectors.attr('checked','checked');
	}
	if( content == 'None' ){
	    datasetsSelectors.removeAttr('checked');
	}
    });


    var fieldsParam = $( "#fields-param" ),
	datasetsParam = $( "#datasets-param" );

    var reloadParams = function(){
	var url_params =
	    '?'+ fieldsParam.attr('data-param') +'=' + ((fieldsParam.prop('checked'))?'true':'false') +
	    '&'+ datasetsParam.attr('data-param') +'=' + ((datasetsParam.prop('checked'))?'true':'false');
	var loc = '//' + location.host + location.pathname;
	window.location.href = loc + url_params;
    }

    fieldsParam.on('change', reloadParams);
    datasetsParam.on('change', reloadParams);

    $(document).keyup(function(e) {
	//console.log('Key Code', e.keyCode);
	if (e.keyCode == 27) { // escape
	    $('#beacon-response-trigger').prop('checked', false);
	    $('#beacon-request-trigger').prop('checked', false);
	}
    });

})();
