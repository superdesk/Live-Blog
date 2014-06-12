define([
	'plugins/wrappup-toggle',
	'plugins/permanent-link',
	'plugins/twitter-widgets',
	'css!theme/liveblog',
	'tmpl!theme/container',
	'tmpl!theme/item/base'
], function(){
	return {
		//enviroments: [ 'mobile', 'desktop', 'quirks' ],
		plugins: [ 'wrappup-toggle', 
					'permanent-link',
					'twitter-widgets'
				]
	}
});