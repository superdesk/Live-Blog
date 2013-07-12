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
	'gizmo/view-events',
	'models/blog'
], function( Gizmo ){
	var blog = new Gizmo.Register.Blog();
		blog.url.decorate('%s/'+liveblog.id);
		blog.sync({force: true});
	if(liveblog.el)
//	$('<div>Hello</div>').insertBefore(liveblog.script); 
});{force: true}