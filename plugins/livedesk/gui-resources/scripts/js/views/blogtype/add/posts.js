define([
    'jquery', 
    'gizmo/superdesk',
    'tmpl!livedesk>blogtype/add/posts'
], function( $, Gizmo) {

    return Gizmo.View.extend({
        tmplData: {},
        init: function(){
            this.render();
            var self = this;
            self.collection
                .off('read update addingspending updatepending', self.render)
                .on('read update addingspending updatepending', self.render, self);
            /*    .xfilter('*')
                .sync();
            */
        },

        render: function(evt, data){
            var self = this,
                posts = this.collection.feed(),
                data = { PostPosts: this.collection.feedPending().concat(posts) };
            $.extend(data, self.tmplData);
            $.tmpl('livedesk>blogtype/add/posts', data, function(e, o){
                self.setElement(o);
            });
        }        
    });
});