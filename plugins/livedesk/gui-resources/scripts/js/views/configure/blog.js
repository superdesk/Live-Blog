 define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'views/languages'),
    config.guiJs('livedesk', 'views/blogtypes'),
    config.guiJs('livedesk', 'views/configure/themes'),
    config.guiJs('livedesk', 'models/blog'),
    'tmpl!livedesk>layouts/livedesk',
    'tmpl!livedesk>configure',
    'tmpl!livedesk>configure/languages'
], function( $, Gizmo, LanguagesView, BlogTypesView, ThemesView) {
   return Gizmo.View.extend({
        events: {
            '[data-action="save"]': { 'click': 'save' },
            '[data-action="save-close"]': { 'click': 'saveClose' },
            '[data-action="cancel"]': { 'click': 'close' }
        },
        init: function() {
            
        },
        save: function(evt){
            var self = this,
                EmbedConfig = {
                    'theme': self.el.find('[name="Theme"]').val()
                },
                data = {
                    Language: self.el.find('[name="Language"]').val(),
                    Type: self.el.find('[name="blogtypeselection"]:checked').val(),
                    EmbedConfig: JSON.stringify(EmbedConfig)
                }
            self.model.set(data).sync();
        },
        saveClose: function(evt) {
            var self = this,
                EmbedConfig = {
                    'theme': self.el.find('[name="Theme"]').val()
                },
                data = {
                    Language: self.el.find('[name="Language"]').val(),
                    Type: self.el.find('[name="blogtypeselection"]:checked').val(),
                    EmbedConfig: JSON.stringify(EmbedConfig)
                }
            self.model.set(data).sync().done(function(){
               self.close(evt);
            });
        },
        close:  function(evt) {
            var self = this;
            $(self.el).find('a[data-target="edit-blog"]').click();
        },
        refresh: function() {
            var self = this;
            self.model = Gizmo.Auth(new Gizmo.Register.Blog(self.theBlog));
            self.model
                .one('read', self.render, self)
                .sync();
        },
        render: function() {
            var self = this,
                themesData,
                embedConfig,
                data = $.extend({}, self.model.feed(), {
                    BlogHref: self.theBlog,
                    ui: 
                    {
                        content: 'is-content=1',
                        side: 'is-side=1',
                        submenu: 'is-submenu',
                        submenuActive2: 'active'
                    }
                });
            $.superdesk.applyLayout('livedesk>configure', data, function() {
            //$.tmpl('livedesk>configure', self.model.feed(), function(e, o){
                //self.el.html(o);
                self.languagesView = new LanguagesView({
                    tmpl: 'livedesk>configure/languages',
                    el: self.el.find('.languages'),
                    _parent: self,
                    tmplData: { selected: self.model.get('Language').get('Id')}
                });
                self.blogtypesView = new BlogTypesView({
                    el: self.el.find('.blogtypes'),
                    _parent: self,
                    theBlog: self.theBlog,
                    tmplData: { selected: self.model.get('Type').get('Id') }
                });
                themesData = {
                    el: self.el.find('.themes'),
                    _parent: self,
                    theBlog: self.theBlog
                };
                if(self.model.get('EmbedConfig')) {
                    embedConfig = JSON.parse(self.model.get('EmbedConfig'));
                    themesData.tmplData = { selected: embedConfig.theme };
                } 
                self.themesView = new ThemesView(themesData);
                // TODO: move this in emebed view or in theme view
                self.el.find('#emebed-script').focus(function() { $(this).select(); } );
                var 
                    topSubMenu = $(self.el).find('[is-submenu]'),
                    content = $(self.el).find('[is-content]');
                $(topSubMenu)
                .off(self.getEvent('click'), 'a[data-target="configure-blog"]')
                .on(self.getEvent('click'), 'a[data-target="configure-blog"]', function(event)
                {
                    event.preventDefault();
                    var blogHref = $(this).attr('href')
                    $.superdesk.getAction('modules.livedesk.configure')
                    .done(function(action)
                    {
                        action.ScriptPath && 
                            require([$.superdesk.apiUrl+action.ScriptPath], function(app){ new app(blogHref); });
                    });
                })
                .off(self.getEvent('click'), 'a[data-target="manage-collaborators-blog"]')
                .on(self.getEvent('click'), 'a[data-target="manage-collaborators-blog"]', function(event)
                {
                    event.preventDefault();
                    var blogHref = $(this).attr('href')
                    $.superdesk.getAction('modules.livedesk.manage-collaborators')
                    .done(function(action)
                    {
                        action.ScriptPath && 
                            require([$.superdesk.apiUrl+action.ScriptPath], function(app){ new app(blogHref); });
                    });
                })
                .off(self.getEvent('click'), 'a[data-target="edit-blog"]')
                .on(self.getEvent('click'), 'a[data-target="edit-blog"]', function(event)
                {
                    event.preventDefault();
                    var blogHref = $(this).attr('href');
                    $.superdesk.getAction('modules.livedesk.edit')
                    .done(function(action)
                    {
                        action.ScriptPath && 
                            require([$.superdesk.apiUrl+action.ScriptPath], function(EditApp){ EditApp(blogHref); });
                    });
                });
            });
        }
    });
});