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
		'jquery': '//ajax.googleapis.com/ajax/libs/jquery/1/jquery.min',
		'jquery.ui': '//ajax.googleapis.com/ajax/libs/jqueryui/1/jquery-ui.min',
		'jquery.ui.ext': config.js_url + '/jquery/ui-ext',
		'dust': config.js_url + '/dust',
		'jquery.tmpl': config.js_url + '/jquery/dust',
		'jquery.rest': config.js_url + '/jquery/rest',
		'history': config.js_url + '/history',
		'history.adapter': config.js_url + '/history/adapter.jquery',
		'jquery.superdesk': config.js_url + '/jquery/superdesk',
		'tmpl': config.js_url + '/require/dustjs'
	}
});

require(['jquery','dust','jquery.tmpl', 'jquery.superdesk', 'lib/core/scripts/js/views/menu'], 
function($, dust, jqueryDust, superdesk, MenuView)
{  
    superdesk.navigation.init();
    var menuView = new MenuView;
}); 