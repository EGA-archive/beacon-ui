(function(){ // scoping

    var message = $('#message');

    var timer;
    var fadeAway = function(){
	timer = setTimeout(function(){ message.addClass('hidden'); }, 5000);
    }

    if( message.hasClass('fadeAway') ){
	fadeAway();
    }

    message.on("mouveover", function() {
	message.removeClass('fadeAway');
	clearTimeout(timer);
    }).on("mouveout", function() {
	message.addClass('fadeAway');
	fadeAway();
    }

})();
