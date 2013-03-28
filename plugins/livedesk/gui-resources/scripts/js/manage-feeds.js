define([
	'jquery',
	'tmpl!livedesk>manage-feeds'
	], function ($) {
	
	$.tmpl('livedesk>manage-feeds',{}, function(e,o){
		$('#area-main').html(o);
	});
});