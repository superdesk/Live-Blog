requirejs.config({
	urlArgs: 'v=110',
	paths: {
		'theme': 'livedesk-embed/themes/cnm'
	}
});
require(['cnm.min'], function() {
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
	var _gaq = _gaq || [];
	_gaq.push(['_setAccount', 'UA-45928067-1']);
	_gaq.push(['_trackPageview']);
	
	(function() {
	var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
	ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
	var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
	})();
});
