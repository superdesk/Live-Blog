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
		'i18n': config.js_url + '/require/i18n',
		'gettext': config.js_url + '/gettext',
	}
});
require(['lib/core/scripts/js/views/menu', 'jquery', 'jquery/superdesk', 'jquery/i18n'], 
function(MenuView, $)
{
    $.superdesk.navigation.init(function(){ var menuView = new MenuView; });
}); 