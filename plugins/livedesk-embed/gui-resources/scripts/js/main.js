/*require([ 
	'jquery',
	'jquery/tmpl',
	'tmpl!theme/container',
], function($){
	$('#livedesk-root').tmpl('theme/container');
});*/
require([
	'css!theme/livedesk',
	'livedesk-embed/views/timeline', 
	'jquery/i18n',
], function(css, TimelineView){
	new TimelineView({ url: livedesk.blog });	
});