 define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'views/languages'),
    config.guiJs('livedesk', 'views/blogtypes'),
    config.guiJs('livedesk', 'models/blog'),
    'tmpl!livedesk>layouts/livedesk',
    'tmpl!livedesk>configure',
    'tmpl!livedesk>configure/languages'
], function( $, Gizmo, LanguagesView, BlogTypesView) {
   return Gizmo.View.extend({
        events: {
            '[data-action="save"]': { 'click': 'save' },
            '[data-action="save-close"]': { 'click': 'saveClose'}
        },
        init: function() {
            
        },
        save: function(evt){
            var self = this,
                data = {
                    Language: self.el.find('[name="Language"]').val(),
                    Type: self.el.find('[name="blogtypeselection"]:checked').val()
                }
            self.model.set(data).sync();
        },
        refresh: function() {
            var self = this;
            self.model = Gizmo.Auth(new Gizmo.Register.Blog(self.theBlog));
            self.model
                .on('read', self.render, self)
                .sync();
        },
        render: function() {
            var self = this;
            $.tmpl('livedesk>configure', self.model.feed(), function(e, o){
                self.el.html(o);
                console.log(o);
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
                var 
                    topSubMenu = $(this.el).find('[is-submenu]'),
                    content = $(this.el).find('[is-content]');
                console.log(topSubMenu);
                $(topSubMenu)
                .off('click'+self.getNamespace(), 'a[data-target="configure-blog"]')
                .on('click'+self.getNamespace(), 'a[data-target="configure-blog"]', function(event)
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
                .off('click'+self.getNamespace(), 'a[data-target="edit-blog"]')
                .on('click'+self.getNamespace(), 'a[data-target="edit-blog"]', function(event)
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