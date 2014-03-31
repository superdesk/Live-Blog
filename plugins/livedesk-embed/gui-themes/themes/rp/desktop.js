define([
	'plugins/button-pagination',
	'plugins/ivw-counter',
	'plugins/post-hash',
	'plugins/twitter-widgets',
	'tmpl!theme/container',
	'tmpl!theme/item/base',
	'css!theme/liveblog'
], function(){
	return {
		plugins: [ 'button-pagination', 'ivw-counter', 'post-hash', 'twitter-widgets' ]
	}
});