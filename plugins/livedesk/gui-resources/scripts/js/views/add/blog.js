 define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'views/languages'),
    config.guiJs('livedesk', 'views/blogtypes'),
   'jqueryui/texteditor',
    'tmpl!livedesk>add' 
], function( $, Gizmo, LanguagesView, BlogTypesView) {
   
   return Gizmo.View.extend({
        init: function() {

        },
        refresh: function() {
            var self = this;
            $.tmpl('livedesk>add', {}, function(e, o){
                self.setElement(o);
                self.languagesView = new LanguagesView({
                    el: self.el.find('.languages'),
                    _parent: self
                });
                self.blogtypesView = new BlogTypesView({
                    el: self.el.find('.blogtypes'),
                    tmplData: { add: true },
                    _parent: self
                });                 
                self.el.modal('show');
            });
        }
    });
});