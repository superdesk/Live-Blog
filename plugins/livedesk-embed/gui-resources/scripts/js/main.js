require([
	'livedesk-embed/views/timeline', 
	'jquery/i18n'
], function( TimelineView ){
	new TimelineView({ url: livedesk.blog });	
});