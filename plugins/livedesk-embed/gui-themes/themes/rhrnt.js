define([
	'plugins/wrappup-toggle',
	'plugins/permanent-link',
	'plugins/user-comments',
	'plugins/twitter-widgets',
    'plugins/pretty-date',    
	'plugins/citizen',
	'plugins/button-pagination',
	'tmpl!theme/container',
	'tmpl!theme/item/base',
	'css!theme/liveblog'
], function(){
	return {
		//enviroments: [ 'mobile', 'desktop', 'quirks' ],
		plugins: [ 'wrappup-toggle', 
					'permanent-link',
					'user-comments',
					'twitter-widgets',
					'citizen',
					'button-pagination']
	}
});