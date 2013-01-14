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
                .off('read update addingspending updatepending', self.render)
                .on('read update addingspending updatepending', self.render, self)
                .xfilter('*')
                .sync();
            console.log('posts: ',self.collection._clientId)
        },

        render: function(evt, data){
            var self = this,
                posts = this.collection.feed(),
                data = { PostPosts: this.collection.feedPending().concat(posts) };
            $.extend(data, self.tmplData);
            $.tmpl('livedesk>blogtype/postposts', data, function(e, o){
                self.setElement(o);
            });
        }        
    });
});