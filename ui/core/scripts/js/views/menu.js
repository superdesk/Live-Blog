define
([
    'jquery','jquery/superdesk', 'gizmo/superdesk', 
    'gizmo/superdesk/action',
    config.cjs('views/auth.js'),
    'router',
    'dust/core','jquery/tmpl','jquery/rest', 'bootstrap',  
    'tmpl!layouts/dashboard',
    'tmpl!navbar'
], 
function($, superdesk, Gizmo, Action, authView, router)
{
    var MenuView = Gizmo.View.extend
    ({
        events: 
        { 
            "[data-logged-in]": { 'click' : 'loginHandler' },
            "#navbar-logout": { 'click' : 'logoutHandler' }
        },
        
        /*!
         * gets menu and renders
         */
        refresh: function()
        {
            this.getMenu(this.render);
        },
        
        getMenu: function(cb)
        {
            var dfd = new $.Deferred,
                self = this;
                dfd.done(cb);

            this.displayMenu = [];
            this.submenus = {};
                
            // get first level of registered menus
            Action.getMore('menu.*').done(function(mainMenus)
            {
                self.displayMenu = [];
                // get submenu level
                Action.getMore('menu.*.*').done(function(subMenus)
                {
                    $(mainMenus).each(function()
                    {
                        // check if main menus have submenus
                        hasSubs = false;
                        for( var i=0; i<subMenus.length; i++ )
                            if( subMenus[i].get('Path').indexOf(this.get('Path')) === 0 ) hasSubs = true;
                        if( hasSubs )
                        {
                            var Subs = 'data-submenu='+this.get('Path'),
                                Subz = '[data-submenu="'+this.get('Path')+'"]';
                            self.submenus[this.get('Path')] = this.get('Path') + '.*';
                        }

                        // set menu data
                        var item = $.extend({}, this.feed(), {
                            Path: this.get('Path').split('.'), 
                            Name: this.get('Path').replace('.', '-'),
                            Subs: Subs
                        });

                        if ('NavBar' in item) {
                            router.route(item.NavBar.substr(1), item.Label, function() {
                                require([item.Script.href], function(app) {
                                    if ('init' in app) {
                                        app.init();
                                    }
                                });
                            });
                        }

                        self.displayMenu.push(item);
                    });

                    dfd.resolve(self);
                });
            }).
            // we still resolve it so we can display something
            fail(function(){ dfd.resolve(self); });

            return this;
        },
        /*!
         * 
         */
        init: function()
        {
            var self = this;
            this.displayMenu = [];
            // refresh menu on login/logout
            $(authView).on('login logout', function(evt){ self.refresh(); });

            this.el.on('refresh-menu', function() { self.refresh(); });
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

            self.el.
                html('').
                tmpl('navbar', navData, function() {
                    // for submenus, we get their corresponding build scripts
                    self.el.find('[data-submenu]').each(function() {
                        var submenuElement = this;
                        Action.initApps(self.submenus[$(this).attr('data-submenu')], submenuElement, self.el);
                    });
                });

            return this;
        },
        /*!
         * login control
         */
        loginHandler: function(evt)
        {
            if( $(evt.currentTarget).attr('data-logged-in') == 'false' ) authView.renderPopup();
        },
        /*!
         * 
         */
        logoutHandler: function(evt)
        {
            authView.logout();
        }
        
        
    });
    
    return MenuView;
});
