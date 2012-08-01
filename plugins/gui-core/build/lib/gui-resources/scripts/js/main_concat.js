requirejs.config
({
        baseUrl: './',
        templatePaths:
            {
                 'default': './temps',
                 'plugin': 'gui/superdesk/{plugin}/templates/'
            },
        waitSeconds: 2,
	paths: 
	{
                'jquery': '.' + '/jquery',
		'jqueryui': '.' + '/jquery/ui',
		'bootstrap': '.' + '/jquery/bootstrap',
		'dust': '.' + '/dust',
		'history': '.' + '/history',
		'utils': '.' + '/utils',
		'gettext': '.' + '/gettext',
                'order': '.' + '/require/order',
		'tmpl': '.' + '/require/tmpl',
		'model': '.' + '/require/model',
                'menupreview' : '.' + '/views/menupreview',
		'i18n': '.' + '/require/i18n'
	}
});
require(['jquery', 'jquery/superdesk', 'jquery/i18n', 'utils/date-sort', 'utils/json_parse','utils/str', 'utils/twitter', 'jquery/bootstrap','jqueryui/ext', 'jquery/i18n'
], 
function()
{   
    requirejs.config
    ({
            baseUrl: config.content_url,
            waitSeconds: 2,
            templatePaths:
            {
                'default': 'lib/core/templates/',
                    'plugin': 'gui/superdesk/{plugin}/templates/',
                    'models': 'gui/superdesk/{plugin}/scripts/js/models/'
            },
            paths: 
            {
                    'jquery': config.js_url + '/jquery',
                    'jqueryui': config.js_url + '/jquery/ui',
                    'bootstrap': config.js_url + '/jquery/bootstrap',
                    'dust': config.js_url + '/dust',
                    'history': config.js_url + '/history',
                    'utils': config.js_url + '/utils',
                    'gettext': config.js_url + '/gettext',
                    'order': config.js_url + '/require/order',
                    'tmpl': config.js_url + '/require/tmpl',
                    'model': config.js_url + '/require/model',
                    'i18n': config.js_url + '/require/i18n',
                    'gizmo': config.js_url + '/gizmo'
            }
    });
});

