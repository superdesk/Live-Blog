requirejs.config({
	paths: 	{
		'theme': '../../themes/stt/mobile'
	}
});
define([
	'tmpl!theme/container',
	'css!theme/liveblog'
], function(){
	return {
		plugins: [ 'scroll', 'pagination' ]
	}
});