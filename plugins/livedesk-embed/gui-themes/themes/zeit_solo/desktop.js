define([
	'jquery/tmpl',
	'tmpl!theme/container',
	'tmpl!theme/item/base',
	'tmpl!theme/item/source/infomercial',

	'plugins/button-pagination',
	'plugins/wrappup-toggle',
	'plugins/permanent-link',
	'plugins/twitter-widgets',
	'css!theme/liveblog'
], function(){
	return {
		//enviroments: [ 'mobile', 'desktop', 'quirks' ],
		plugins: [	'button-pagination',
					'wrappup-toggle', 
					'permanent-link',
					'twitter-widgets']
	}
});