requirejs.config
({
	baseUrl: config.content_url,
//	urlArgs: "bust=" +  (new Date).getTime(),
	waitSeconds: 15,
    templatePaths:
	{
	    'default': 'lib/core/templates/',
		'plugin': 'lib/{plugin}/templates/',
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
		'gizmo': config.js_url + '/gizmo',
		'newgizmo': config.js_url + '/newgizmo'		
	}
});
require(['lib/core/scripts/js/views/menu', 'jquery', 'jquery/superdesk', 'jquery/i18n', 'jqueryui/ext'], 
function(MenuView, $, superdesk)
{
    var makeMenu = function(){ var menuView = new MenuView; }, 
    authLock = function()
    {
        var args = arguments,
            self = this;
        require(['lib/core/scripts/js/views/auth'], function(AuthApp)
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
        ajax.fail(function(resp){ resp.status == 401 && authLock.apply(self, arguments); });
        
        return ajax;
    };
    
    $.rest.prototype.config.apiUrl = config.api_url;
    $.restAuth.prototype.config.apiUrl = config.api_url;

    if( localStorage.getItem('superdesk.login.id') )
    {
        $.restAuth.prototype.requestOptions.headers.Authorization = localStorage.getItem('superdesk.login.id');
        superdesk.login = {Id: localStorage.getItem('superdesk.login.id'), Name: localStorage.getItem('superdesk.login.name'), EMail: localStorage.getItem('superdesk.login.email')}
    }
    
    $.superdesk.navigation.init(makeMenu);
});

