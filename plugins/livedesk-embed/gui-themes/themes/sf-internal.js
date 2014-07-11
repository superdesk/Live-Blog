define([
    'plugins/scroll-pagination',
	'plugins/wrappup-toggle',
	'plugins/permanent-link',
	'plugins/twitter-widgets',
	'css!theme/liveblog',
	'tmpl!theme/container',
	'tmpl!theme/item/base',
	'tmpl!theme/item/source/youtube'
], function(){
	return {
		plugins: [
            'scroll-pagination',
            'wrappup-toggle', 
			'permanent-link',
			'twitter-widgets'
		]
	}
});