define([
	'plugins/wrappup-toggle',
	'plugins/pagination',
	'plugins/permanent-link',
	'css!theme/liveblog'
], function(){
	return {
		//enviroments: [ 'mobile', 'desktop', 'quirks' ],
		plugins: [ 'scroll', 'pagination' ]
	}
});