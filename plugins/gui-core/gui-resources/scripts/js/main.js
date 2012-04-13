requirejs.config
({
	baseUrl: config.content_url,
	urlArgs: "bust=" +  (new Date).getTime(),
	templatePaths: 
	{
	    'default': 'lib/core/templates/',
		'plugin': 'gui/superdesk/{plugin}/templates/'
	},
	paths: 
	{
		'jquery': config.js_url + '/jquery',
		'jqueryui': config.js_url + '/jquery/ui/',
		'dust': config.js_url + '/dust',
		'history': config.js_url + '/history',
		'tmpl': config.js_url + '/require/tmpl'
	}
});

require(['jquery','dust','jquery/tmpl', 'jquery/superdesk', 'lib/core/scripts/js/views/menu'], 
function($, dust, jqueryDust, superdesk, MenuView)
{  
	superdesk.navigation.init();
    var menuView = new MenuView;
}); 