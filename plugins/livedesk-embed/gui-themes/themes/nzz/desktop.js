define([
	'plugins/button-pagination',
	'plugins/post-hash',
	'plugins/twitter-widgets',
    'plugins/permanent-link',    
	'tmpl!theme/container',
	'tmpl!theme/item/base',
	'css!theme/liveblog'
], function(){
	return {
		plugins: [ 'button-pagination', 'post-hash', 'twitter-widgets', 'permanent-link' ]
	}
});