requirejs.config
({
	baseUrl: 'http://localhost:8080/content/lib/',
	waitSeconds: 15,
	paths: 
	{
		'core': 'core/scripts/js/',
		'livedesk-embed': 
		'jquery': 'core/jquery',
		'jqueryui': config.cjs('jquery/ui'),
		'bootstrap': config.cjs('jquery/bootstrap'),
		'dust': config.cjs('dust'),
		'history': config.cjs('history'),
		'utils': config.cjs('utils'),
		'gettext': config.cjs('gettext'),
        'order': config.cjs('require/order'),
		'tmpl': config.cjs('require/tmpl'),
		'model': config.cjs('require/model'),
		'i18n': config.cjs('require/i18n'),
		'gizmo': config.cjs('gizmo'),
		'concat': config.cjs('concat'),		
		'newgizmo': config.cjs('newgizmo')		
	}
});

require(['jquery'], function($){
	console.log('loaded');
});