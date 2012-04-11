define([
    'jquery','jquery.superdesk','jquery.tmpl','jquery.rest', 
    'tmpl!layouts/dashboard',
    'tmpl!navbar'
], function($, superdesk)
{
    var MenuView = function() 
    {
        superdesk.apiUrl = config.api_url;
        
        var menu = new $.rest(superdesk.apiUrl + '/resources/GUI/Action?path=menu.*')
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
    		    superdesk.navigation.bind($(this).attr('href'), function()
    		    {
    		        require([superdesk.apiUrl+'/'+$(this).attr('href')]);
    		    });
    			event.preventDefault(); 
    		});
    		
        });
        $('#area-main').tmpl( 'layouts/dashboard' );
    }

    return MenuView;
});