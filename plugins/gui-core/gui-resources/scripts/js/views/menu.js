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
        var menu = new $.rest(config.api_url + '/resources/GUI/Action?path=menu.*')
        .done(function(menu)
        {  
    		var displayMenu = []
    		$(menu).each(function()
    		{ 
    		    var Subs = null;
    			if(this.ChildrenCount > 0)
    			{
    			    Subs = 'data-submenu='+this.Path;
    			    Subz = '[data-submenu="'+this.Path+'"]';
    			    new $.rest(config.api_url + '/resources/GUI/Action?path=' + this.Path + '.*')
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
    		
    		$('#navbar-top')
    		.tmpl( 'navbar', {superdesk: {menu: displayMenu}} )
    		.on('click', '.nav a', function(event)
    		{
    		    if(!$(this).attr('href')) return;
    		    var self = this;
    		    superdesk.navigation.bind
    		    ( 
    		        $(this).attr('href'), 
    		        function(){ require([config.api_url + $(self).attr('script-path')], 
    		            function(x)
    		            { 
    		                if(x && x.init) x.init(); 
    		            });
    		        }
    		    );
    			event.preventDefault(); 
    		});
    		
        });
        $('#area-main').tmpl( 'layouts/dashboard' );
    };

    return MenuView;
});