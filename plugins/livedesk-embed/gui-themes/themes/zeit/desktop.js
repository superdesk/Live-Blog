define([
	'jquery/tmpl',
	'plugins/button-pagination',
	'plugins/post-hash',
	'tmpl!theme/container',
	'tmpl!theme/item/base',
	'css!theme/liveblog'
], function(){
	return {
		plugins: [ 'button-pagination', 'post-hash' ]
	}
});