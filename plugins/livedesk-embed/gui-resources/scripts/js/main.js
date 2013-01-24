require([
	'jquery',
	'livedesk-embed/views/timeline', 
	'jquery/i18n'
], function( $, TimelineView ){
	var data = { url: livedesk.blog };
	if( livedesk.el !== undefined) {
		if($(livedesk.el).length !== 0)
			data.el = livedesk.el;
		else
			console.log('Element: ',livedesk.el,' not found!');
	}
	new TimelineView(data);	
});