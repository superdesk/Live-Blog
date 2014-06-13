define([
	'plugins/button-pagination',
	'plugins/wrappup-toggle',
	'plugins/permanent-link',
	'plugins/twitter-widgets',
    'plugins/pretty-date',
	'tmpl!theme/container',
	'tmpl!theme/item/base',
	'css!theme/liveblog'
], function(){
	return {
		//enviroments: [ 'mobile', 'desktop', 'quirks' ],
		plugins: ['button-pagination',
					'wrappup-toggle', 
					'permanent-link',
					'twitter-widgets']
	}
});