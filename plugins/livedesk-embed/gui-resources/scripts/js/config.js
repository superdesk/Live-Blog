requirejs.config({
	baseUrl: 'http://localhost:8080/content/lib/',
	paths: 
	{
		'livedesk-embed': 'livedesk-embed/scripts/js/',
		'livedesk-embed/templates': 'livedesk-embed/templates',
		
		'tmpl': 'livedesk-embed/scripts/js/core/require/tmpl',
		'i18n': 'livedesk-embed/scripts/js/core/require/i18n',
		
		'jquery': 'livedesk-embed/scripts/js/core/jquery',
		'dust': 'livedesk-embed/scripts/js/core/dust',
		'utils': 'livedesk-embed/scripts/js/core/utils',
		'gettext': 'livedesk-embed/scripts/js/core/gettext',
		'gizmo': 'livedesk-embed/scripts/js/core/gizmo',
		'jquery': 'livedesk-embed/scripts/js/core/jquery'
	}/*,
	map: {
		'gizmo/superdesk': {
			'gizmo': 'gizmo'
		}
	}*/
});
