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
		'utils': config.js_url + '/utils',
		'gettext': config.js_url + '/gettext',
		'tmpl': config.js_url + '/require/tmpl',
		'i18n': config.js_url + '/require/i18n'
	}
});
require(['lib/core/scripts/js/views/menu', 'jquery', 'jquery/superdesk', 'jquery/i18n', 'jqueryui/ext'], 
function(MenuView, $)
{
    $.rest.prototype.config.apiUrl = config.api_url;
    $.restAuth.prototype.config.apiUrl = config.api_url;
    
    $.superdesk.navigation.init(function(){ var menuView = new MenuView; });
}); 