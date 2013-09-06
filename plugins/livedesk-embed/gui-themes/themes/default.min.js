define([
	'plugins/wrappup-toggle',
	'plugins/scroll-pagination',
	'plugins/permanent-link',
	'plugins/user-comments',
	'css!theme/liveblog'
], function(){
	return {
		//enviroments: [ 'mobile', 'desktop', 'quirks' ],
		plugins: [ 'wrappup-toggle', 
					'scroll-pagination', 
					'permanent-link',
					'user-comments' ]
	}
});