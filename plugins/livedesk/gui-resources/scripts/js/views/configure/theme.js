 define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'model/theme'), 
    'tmpl!livedesk>configure/theme',
], function( $, Gizmo, PostPostsView ) {
   return Gizmo.View.extend({
        tmplData: {},
        tagName: 'option',
        namespace: 'livedesk',
        events: {
        },
        init: function(){
            var self = this;
            self.render();
        },
        render: function(evt, data){
            var self = this, 
                el,
                data = { Themes: self.model.feed() };
            $.extend( data, self.tmplData );
            $.tmpl('livedesk>configure/theme', data, function(e,o){
                self.setElement(o);
            });
        }
    });
});