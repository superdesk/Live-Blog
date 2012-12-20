 define([
    'jquery', 
    'gizmo/superdesk',
    'tmpl!livedesk>blogtype/postposts'
], function( $, Gizmo) {

    return Gizmo.View.extend({
        tmplData: {},
        init: function(){
            var self = this;
            self.collection
                .on('read update', self.render, self)
                .xfilter('*')
                .sync();
        },
        render: function(evt, data){
            var self = this, data = { PostPosts: this.collection.feed() };
            $.extend(data, self.tmplData);
            $.tmpl('livedesk>blogtype/postposts', data, function(e, o){
                self.setElement(o);
            });
        }        
    });
});