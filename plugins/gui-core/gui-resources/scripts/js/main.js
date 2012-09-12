requirejs.config
({
	baseUrl: config.content_url,
//	urlArgs: "bust=" +  (new Date).getTime(),
	waitSeconds: 15,
    templatePaths:
	{
	    'default': config.core('')+'templates/',
		'plugin': config.gui('{plugin}/templates/')
	},
	paths: 
	{
		'jquery': config.cjs('jquery'),
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
require(['concat'], function(){
	require([config.cjs('views/menu.js'), 'jquery', 'jquery/superdesk', 'jquery/i18n', 'jqueryui/ext'], 
	function(MenuView, $, superdesk)
	{
		var makeMenu = function()
		{ 
		    var menuView = new MenuView;
		}, 
		authLock = function()
		{
			var args = arguments,
				self = this;
			require([config.core()+'scripts/js/views/auth'], function(AuthApp)
			{
				AuthApp.success = makeMenu;
				AuthApp.require.apply(self, arguments); 
			});
		},
		r = $.rest.prototype.doRequest;
		$.rest.prototype.doRequest = function()
		{
			var ajax = r.apply(this, arguments),
				self = this;
			ajax.fail(function(resp){ (resp.status == 404 || resp.status == 401) && authLock.apply(self, arguments); });
			return ajax;
		};

		$.rest.prototype.config.apiUrl = config.api_url;
		$.restAuth.prototype.config.apiUrl = config.api_url;

		if( localStorage.getItem('superdesk.login.id') )
		{
			$.restAuth.prototype.requestOptions.headers.Authorization = localStorage.getItem('superdesk.login.session');
			superdesk.login = {Id: localStorage.getItem('superdesk.login.id'), Name: localStorage.getItem('superdesk.login.name'), EMail: localStorage.getItem('superdesk.login.email')}
		}

		$.superdesk.navigation.init(makeMenu);
	});
});