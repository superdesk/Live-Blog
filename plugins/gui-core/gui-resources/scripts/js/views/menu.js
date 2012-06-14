define
([
    'jquery','jquery/superdesk','dust/core','jquery/tmpl','jquery/rest', 'bootstrap',  
    'tmpl!layouts/dashboard',
    'tmpl!navbar'
], 
function($, superdesk, dust)
{
    var MenuView = function() 
    {
        superdesk.getActions('menu.*')
        .done(function(menu)
        {  
    		var displayMenu = [],
    		    refreshMenu = function() 
    		{
    		    displayMenu = [];
        		$(menu).each(function()
        		{ 
        		    var Subs = null;
        			if(this.ChildrenCount > 0)
        			{
        			    Subs = 'data-submenu='+this.Path;
        			    Subz = '[data-submenu="'+this.Path+'"]';
        			    superdesk.getActions(this.Path + '.*')
        			    .done(function(subs)
        			    { 
        			        $(subs).each(function()
        			        { 
        			            require([config.api_url + this.ScriptPath], function(x){ x.init(Subz); }); 
        			        });
        			    });
        			}
        			displayMenu.push($.extend({}, this, 
        			{ 
        			    Path: this.Path.split('.'), 
        			    Name: this.Path.replace('.', '-'),
        			    Subs: Subs
        			}));
        		});
        		
        		var navData = {superdesk: {menu: displayMenu}};
        		superdesk.login && $.extend(navData, {user: superdesk.login});
        		$('#navbar-top')
        		.tmpl( 'navbar', navData )
        		.off('click.superdesk')
        		.on('click.superdesk', '.nav a', function(event)
        		{
        		    var self = this;
        		    if(!$(self).attr('href')) return;
        		    if(!$(self).attr('script-path')) { event.preventDefault(); return; }

        		    $(self).attr('data-loader') != 'false' && superdesk.showLoader();
        		    
        		    superdesk.navigation.bind
        		    ( 
        		        $(self).attr('href'), 
        		        function(){ require([config.api_url + $(self).attr('script-path')], 
        		            function(x)
        		            { 
        		                x && x.init && x.init(); 
        		            });
        		        }
        		    );
        			event.preventDefault(); 
        		});
        		$('#navbar-logout', $('#navbar-top'))
        		.off('click.superdesk')
        		.on('click.superdesk', function()
        		{
        		    delete superdesk.login;
        		    localStorage.removeItem('superdesk.login.name');
        		    localStorage.removeItem('superdesk.login.id');
        		    delete $.restAuth.prototype.requestOptions.headers.Authorization;
        		    new MenuView;
        		});
    		};
    		$('#navbar-top').on('refresh-menu', refreshMenu);
    		refreshMenu();
    		
        });
        $.superdesk.applyLayout('layouts/dashboard');
    };

    return MenuView;
});