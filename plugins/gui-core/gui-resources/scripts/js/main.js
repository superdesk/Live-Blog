requirejs.config({
	baseUrl: config.content_url,
	templatePaths: {
		'default': 'lib/core/scripts/js/tmpl/',
		'plugin': 'gui/superdesk/{plugin}/tmpl/'
	},
	paths: {
		'jquery':    '//ajax.googleapis.com/ajax/libs/jquery/1/jquery.min',
		'jquery.ui': '//ajax.googleapis.com/ajax/libs/jqueryui/1/jquery-ui.min',
		'jquery.ui.ext': config.js_url + '/libs/jquery/jquery-ui-ext.js',
		'dust': config.js_url + '/libs/dust/0.3.0/dust',
		'jquery.tmpl': config.js_url + '/libs/dust/jquery-dust',
		'jquery.rest': config.js_url + '/libs/jquery/jquery-rest',
		'jquery.superdesk': config.js_url + '/libs/jquery/jquery-superdesk',
		'tmpl': config.js_url + '/libs/require/dustjs',
	},
});

require(['jquery','dust','jquery.tmpl', 'lib/core/scripts/js/views/menu',], function($, dust, jqueryDust, MenuView){  
  var menuView = new MenuView;
}); 