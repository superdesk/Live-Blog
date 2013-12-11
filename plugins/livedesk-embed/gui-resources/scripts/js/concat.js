requirejs.config({
	baseUrl: '/content/lib/',
	paths: 	{
		'livedesk-embed': 'scripts/js/',
		'jquery': 'scripts/js/core/jquery',
		'tmpl': 'scripts/js/core/require/tmpl',
		'tmpl-build': 'scripts/js/core/require/tmpl-build',
		'css': 'scripts/js/core/require/css',
		'i18n': 'scripts/js/core/require/i18n',

		'dust': 'scripts/js/core/dust',
		'utils': 'scripts/js/core/utils',
		'gettext': 'scripts/js/core/gettext',
		'gizmo': 'scripts/js/core/gizmo',

		'window': 'scripts/js/core/window',
		'document': 'scripts/js/core/document'
	}
});

require([
	'jquery',
	'livedesk-embed/views/timeline',
	'livedesk-embed/views/user-comments-popup',
	'livedesk-embed/plugins',
	'jquery/cookie'
], function(){});
