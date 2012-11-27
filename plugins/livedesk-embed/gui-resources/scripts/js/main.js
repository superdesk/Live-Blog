/*require([ 
	'jquery',
	'jquery/tmpl',
	'tmpl!theme/container',
], function($){
	$('#livedesk-root').tmpl('theme/container');
});*/
require([ 'livedesk-embed/views/timeline', 'jquery/i18n' ], function(TimelineView){
	new TimelineView({ url: livedesk.blog });
	
});