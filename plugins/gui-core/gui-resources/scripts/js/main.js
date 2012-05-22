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
        'order': config.js_url + '/require/order',
		'tmpl': config.js_url + '/require/tmpl',
		'i18n': config.js_url + '/require/i18n'
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

    console.log(localStorage.getItem('superdesk.login.id'));
    if( localStorage.getItem('superdesk.login.id') )
    {
        $.restAuth.prototype.requestOptions.headers.Authorization = localStorage.getItem('superdesk.login.id');
        superdesk.login = {Id: localStorage.getItem('superdesk.login.id'), Name: localStorage.getItem('superdesk.login.name')}
    }
    
    $.superdesk.navigation.init(makeMenu);
});

