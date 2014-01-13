define([
	'jquery/tmpl',
	'plugins/button-pagination',
	'plugins/post-hash',
	'plugins/twitter-widgets',
	'tmpl!theme/container',
	'tmpl!theme/item/base',
	'css!theme/liveblog'
], function(){
	return {
		plugins: [ 'button-pagination', 'post-hash', 'twitter-widgets' ]
	}
});