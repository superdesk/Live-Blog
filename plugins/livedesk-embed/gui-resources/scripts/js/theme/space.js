requirejs.config({
	paths: {
		'theme': 'livedesk-embed/templates/space'
	}
});
require(['../config'], function(){
	require(['livedesk-embed/main']);
});