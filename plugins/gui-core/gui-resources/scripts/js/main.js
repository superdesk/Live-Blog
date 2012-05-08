requirejs.config
({
	baseUrl: config.content_url,
//	urlArgs: "bust=" +  (new Date).getTime(),
	templatePaths: 
	{
	    'default': 'lib/core/templates/',
		'plugin': 'gui/superdesk/{plugin}/templates/'
	},
	paths: 
	{
		'jquery': config.js_url + '/jquery',
		'jqueryui': config.js_url + '/jquery/ui',
		'bootstrap': config.js_url + '/jquery/bootstrap',
		'dust': config.js_url + '/dust',
		'history': config.js_url + '/history',
		'tmpl': config.js_url + '/require/tmpl',
		'gettext': config.js_url + '/gettext',
	}
});

require(['jquery/superdesk', 'lib/core/scripts/js/views/menu'], //, 'jquery/i18n', 'lib/core/scripts/catalog' ], 
function(superdesk, MenuView)//, I18n, catalog)
{
	//I18n.load(catalog);
    superdesk.navigation.init(function(){ var menuView = new MenuView; });
}); 