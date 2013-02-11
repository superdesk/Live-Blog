requirejs.config({
	paths: {
		'theme': 'livedesk-embed/themes/default'
	}
});
require(['default.min'], function() {
	require(['../scripts/js/config'], function(){
		var name;
		for(name in livedesk.theme) {
			define('tmpl!theme/'+name, ['dust/compiler'], function(dust){
				dust.loadSource(dust.compile(livedesk.theme[name],'theme/'+name));
			});		
		}
		require(['css!theme/livedesk', 'livedesk-embed/main']);
	});
});