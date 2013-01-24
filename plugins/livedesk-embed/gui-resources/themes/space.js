requirejs.config({
	paths: {
		'theme': 'livedesk-embed/themes/space'
	}
});
require(['../config'], function(){
	var name;
	for(name in livedesk.theme) {
		define('tmpl!theme/'+name, ['dust/compiler'], function(dust){
			dust.loadSource(dust.compile(livedesk.theme[name],'theme/'+name));
		});		
	}
	require(['livedesk-embed/main']);
});