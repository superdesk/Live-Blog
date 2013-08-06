requirejs.config({
	paths: 	{
		'theme': '../../themes/stt/quirks'
	}
});
define([
	'tmpl!theme/container',
	'tmpl!theme/item/base',
	'css!theme/liveblog'
], function(){
	return {
		plugins: [ 'scroll', 'pagination' ]
	}
});