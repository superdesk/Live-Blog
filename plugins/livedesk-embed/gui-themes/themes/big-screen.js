requirejs.config({
	urlArgs: 'v=7',
	paths: {
		'theme': 'livedesk-embed/themes/big-screen'
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
		function loadCss(url) {
			var link = document.createElement("link");
			link.type = "text/css";
			link.rel = "stylesheet";
			link.href = url;
			document.getElementsByTagName("head")[0].appendChild(link);
		}
		loadCss(require.toUrl('theme/livedesk.css'));//'css!theme/livedesk',
		require(['livedesk-embed/main']);
	});
});
