var requirejs;
liveblog.version = 6;// = {Version};
if( window && (window.location.href.indexOf('liveblog-debug') !== -1) 
	&& (window['localStorage'] !== null) && window['localStorage'].getItem('liveblog-debug') ) {
	var loadJs = liveblog.loadJs, script = liveblog.script;
	liveblog = 	JSON.parse(window['localStorage'].getItem('liveblog-debug'));
	liveblog.loadJs = loadJs;
	liveblog.script = script;
}
liveblog.runner = function() {
	requirejs = {
		baseUrl: this.baseUrl,
		urlArgs: 'version=' + this.version
	}
	//this.loadJs('//cdnjs.cloudflare.com/ajax/libs/require.js/2.1.6/require.min.js').setAttribute('data-main','main');
	this.loadJs('core/require').setAttribute('data-main','main');
}
liveblog.runner();
