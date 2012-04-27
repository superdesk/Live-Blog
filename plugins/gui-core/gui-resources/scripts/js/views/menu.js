define
([
    'jquery','jquery/superdesk','dust/core','jquery/tmpl','jquery/rest',
    'tmpl!layouts/dashboard',
    'tmpl!navbar'
], 
function($, superdesk, dust)
{
    var MenuView = function() 
    {
        var menu = new $.rest(config.api_url + '/resources/GUI/Action?path=menu.*')
        .done(function(menu)
        {  
    		var displayMenu = []
    		$(menu).each(function()
    		{ 
    			displayMenu.push($.extend({}, this, { Path: this.Path.split('.'), DisplayName: this.Path.replace('.', '-') }));
    		});
    		$('#navbar-top')
    		.tmpl( 'navbar', {superdesk: {menu: displayMenu}} )
    		.on('click', '.nav a', function(event)
    		{
    		    var self = this;
    		    superdesk.navigation.bind( $(this).attr('href'), require([config.api_url + $(self).attr('script-path')], function(x){ x.init(); }) );
    			event.preventDefault(); 
    		});
    		
        });
        $('#area-main').tmpl( 'layouts/dashboard' );
    };

    return MenuView;
});