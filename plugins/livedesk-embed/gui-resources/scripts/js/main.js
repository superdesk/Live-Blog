require(['livedesk-embed/concat.min'], function(){
	require([
		'jquery',
		'livedesk-embed/views/timeline',
		'jquery/cookie'
	], function( $, TimelineView ){
		var data = { url: livedesk.blog };
		if(livedesk.language) {
			$.cookie('superdesk.langcode',livedesk.language);
		}
		if( livedesk.el !== undefined) {
			if($(livedesk.el).length !== 0)
				data.el = livedesk.el;
			else
				console.log('Element: ',livedesk.el,' not found!');
		}
		new TimelineView(data);	
	});
});