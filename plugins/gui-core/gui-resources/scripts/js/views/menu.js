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
        getMenu: function(cb)
        {
            this.displayMenu = [];
            this.submenus = {};
            
            var dfd = new $.Deferred,
                self = this;
            dfd.done(cb); // attach callback to deferred
            
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
                        
                        self.submenus[this.Path] = this.Path + '.*';
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
            return this;
        },
        init: function()
        {
            var self = this;
            this.setElement($('#navbar-top'));
            this.displayMenu = [];
            this.getMenu(this.render);
            
            this.el.on('refresh-menu', function(){ self.getMenu(self.render); });
            
            $(AuthApp).on('authenticated', function(){ self.getMenu(self.render); });
            $(AuthApp).on('authlock', function()
            { 
                $('[data-username-display="true"]', self.el).text(_('Anonymous'));
            });
            
            $.superdesk.applyLayout('layouts/dashboard');
        },
        /*!
         * Deferred callback
         */
        render: function(view)
        {
            // make data for menu template
            var self = view,
                navData = {superdesk: {menu: self.displayMenu}};
            superdesk.login && $.extend(navData, {user: superdesk.login});
            
            self.el
            .html('')
            .tmpl('navbar', navData, function()
            {
                /*!
                 * for submenus, we get their corresponding build scripts
                 */
                self.el.find('[data-submenu]').each(function()
                {
                    var submenuElement = this;
                    superdesk.getActions( self.submenus[$(this).attr('data-submenu')] )
                    .done(function(subs)
                    {
                        $(subs).each(function()
                        { 
                            require([config.api_url + this.ScriptPath], function(submenuApp)
                            { 
                                submenuApp && submenuApp.init && submenuApp.init(submenuElement, self.el); 
                            }); 
                        });
                    });
                });
            })
            .off('click.superdesk')
            .on('click.superdesk', '.nav > li > a', function(event)
            {
                var self = this;
                if(!$(self).attr('href')) return;
                if(!$(self).attr('script-path')) { event.preventDefault(); return; }

                $(self).attr('data-loader') != 'false' && superdesk.showLoader();
                
                var callback = function()
                { 
                    require([config.api_url + $(self).attr('script-path')], function(x){ x && x.init && x.init(); });
                };
                  
                var href = $(self).attr('href').replace(/^\/+|\/+$/g, '');
                if( $.trim(href) != '' )
                    superdesk.navigation.bind( href, callback, $(self).text() || null );
                else
                    callback();
                
                event.preventDefault(); 
            });
            
            /*!
             * redirect to current page on reload
             */
            if( superdesk.navigation.getStartPathname() != '')
                self.el.find('li > a[href]').each(function()
                {
                    if( $(this).attr('href').replace(/^\/+|\/+$/g, '') == superdesk.navigation.getStartPathname()) 
                        $(this).trigger('click'); 
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
                var gm = self.getMenu(self.render);
            });
        }
        
    });
    
    return MenuView;
});