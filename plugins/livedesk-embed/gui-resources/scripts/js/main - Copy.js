require(['livedesk-embed/concat.min'], function(){
	require([
		'jquery'
	], function( $ ){
		var data = { url: livedesk.blog };
		if( livedesk.el !== undefined) {
			if($(livedesk.el).length !== 0)
				data.el = livedesk.el;
			else
				console.log('Element: ',livedesk.el,' not found!');
		}

		var timeline = new TimelineView(data);

	});
});
