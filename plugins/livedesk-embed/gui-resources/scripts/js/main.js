//require(['concat.min'], function(){
requirejs.config({
	paths: 	{
		'tmpl': 'core/require/tmpl',
		'css': 'core/require/css',
		'i18n': 'core/require/i18n',
		
		'jquery': [
			'//ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min',
			'core/jquery'
		],
		'dust': 'core/dust',
		'utils': 'core/utils',
		'gettext': 'core/gettext',
		'gizmo': 'core/gizmo',
	}
});
require([
	'gizmo/superdesk',
	'models/blog'
], function( Gizmo ){
	// var blogUrl = liveblog.frontendServer + 'resources/LiveDesk/Blog' + liveblog.id = 1;
	// 	this.script = d.scripts[d.scripts.length - 1];
	// 	 = '//tageswoche.com:8080/';
	var blog = new Gizmo.Register.Blog();
		blog.url.decorate('%s/'+liveblog.id);
		console.log(blog.url.get());
		blog.sync();
//	$('<div>Hello</div>').insertBefore(liveblog.script);
});