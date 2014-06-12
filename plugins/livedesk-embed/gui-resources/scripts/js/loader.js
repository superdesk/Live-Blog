var requirejs, require;
//liveblog.version = '2.1.8'; requirejs version
if( window && (window.location.href.indexOf('liveblog-debug') !== -1) 
	&& (window['localStorage'] !== null) && window['localStorage'].getItem('liveblog-debug') ) {
	var loadJs = liveblog.loadJs, script = liveblog.script;
	liveblog = 	JSON.parse(window['localStorage'].getItem('liveblog-debug'));
	liveblog.loadJs = loadJs;
	liveblog.script = script;
}

liveblog.runner = function() {
	this.loadJs('version')
}
liveblog.callbackVersion = function(ver) {
	window.require = window.requirejs = {
		baseUrl: this.baseUrl,
		urlArgs: 'version=' + ver.major + '.' + ver.minor + '.' + ver.revision
	}
	//this.loadJs('//cdnjs.cloudflare.com/ajax/libs/require.js/2.1.6/require.min.js').setAttribute('data-main','main');
	this.loadJs('core/require').setAttribute('data-main','main');	
}
liveblog.runner();
