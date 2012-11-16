define('providers/instagram', [
    'providers',
    'jquery',
    'jquery/jsonp',
    'jquery/tmpl',
    'jqueryui/draggable',
    'providers/instagram/adaptor',
    'tmpl!livedesk>providers/instagram',
    'tmpl!livedesk>providers/instagram/image-item',
    'tmpl!livedesk>providers/load-more',
    'tmpl!livedesk>providers/no-results',
    'tmpl!livedesk>providers/loading'
], function( providers,  $ ) {
	$.extend(providers.instagram, {
		self : this, 
		init : function() {
			
		}
	});
	return providers;
});