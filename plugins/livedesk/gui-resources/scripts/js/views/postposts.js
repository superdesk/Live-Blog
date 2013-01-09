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
                .off('read update clientupdate', self.render)
                .on('read update clientupdate', self.render, self)
                .xfilter('*')
                .sync();
        },

        render: function(evt, data){
            var self = this,
                posts = this.collection.feed(),
                data = { PostPosts: posts.concat(this.collection.feedPending()) };
            console.log('posts: ',posts.concat(this.collection.pendingPosts));
            $.extend(data, self.tmplData);
            $.tmpl('livedesk>blogtype/postposts', data, function(e, o){
                self.setElement(o);
            });
        }        
    });
});