define
([
    'jquery','jquery/superdesk', 'gizmo/superdesk', 
    config.lib_js_urn + 'views/auth',
    'dust/core','jquery/tmpl','jquery/rest', 'bootstrap',  
    'tmpl!layouts/dashboard',
    'tmpl!navbar'
], 
function($, superdesk, Gizmo, AuthApp)
{
    var MenuView = Gizmo.View.extend
    ({
        getMenu: function()
        {
            this.displayMenu = [];
            
            var dfd = new $.Deferred,
                self = this;
            superdesk.getActions('menu.*')
            .done(function(menu)
            {
                $(menu).each(function()
                {
                    var Subs = null;
                    if(this.ChildrenCount > 0)
                    {
                        var Subs = 'data-submenu='+this.Path,
                            Subz = '[data-submenu="'+this.Path+'"]';
                        superdesk.getActions(this.Path + '.*')
                        .done(function(subs)
                        {
                            $(subs).each(function()
                            { 
                                require([config.api_url + this.ScriptPath], function(x){ 
                                    console.log(Subz, $(Subz, self.el), self.el);
                                    x && x.init && x.init(Subz); }); 
                            });
                        });
                    }
                    self.displayMenu.push($.extend({}, this, 
                    { 
                        Path: this.Path.split('.'), 
                        Name: this.Path.replace('.', '-'),
                        Subs: Subs
                    }));
                });
                dfd.resolve(self);
            });
            return dfd;
        },
        init: function()
        {
            var self = this;
            this.setElement($('#navbar-top'));
            this.displayMenu = [];
            this.getMenu().done(this.render);
            
            this.el.on('refresh-menu', function(){ self.getMenu().done(self.render); });
            
            $(AuthApp).on('authenticated', function(){ self.getMenu().done(self.render); });
        },
        /*!
         * Deferred callback
         */
        render: function(view)
        {
            // make data for menu template
            var self = view,
                navData = {superdesk: {menu: self.displayMenu}}
                ;
            superdesk.login && $.extend(navData, {user: superdesk.login});
            
            self.el
            .html('')
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
            
            $('#navbar-logout', self.el) // TODO param.
            .off('click.superdesk')
            .on('click.superdesk', function()
            {
                delete superdesk.login;
                localStorage.removeItem('superdesk.login.name');
                localStorage.removeItem('superdesk.login.id');
                delete $.restAuth.prototype.requestOptions.headers.Authorization;
                $(AuthApp).trigger('logout');
                self.getMenu().done(this.render);
            });
        }
        
    }),
    
    _MenuView = function() 
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
        			    var Subs = 'data-submenu='+this.Path,
        			        Subz = '[data-submenu="'+this.Path+'"]';
        			    superdesk.getActions(this.Path + '.*')
        			    .done(function(subs)
        			    {
        			        $(subs).each(function()
        			        { 
        			            require([config.api_url + this.ScriptPath], function(x){ x && x.init && x.init(Subz); }); 
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
        		    
        		    $(AuthApp).trigger('logout');
        		    
        		    new _MenuView;
        		});
    		}; // refreshMenu
    		
    		
    		$('#navbar-top').on('refresh-menu', refreshMenu);
    		$(AuthApp).off('authenticated').on('authenticated', refreshMenu );
    		refreshMenu();
    		
        });
        $.superdesk.applyLayout('layouts/dashboard');
    };
    
    return MenuView;
});