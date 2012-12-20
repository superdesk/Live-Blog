 define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'views/postposts'), 

    'tmpl!livedesk>blogtype/blogtype',
], function( $, Gizmo, PostPostsView ) {
   
   return Gizmo.View.extend({
        tmplData: {},
        tagName: 'li',
        namespace: 'livedesk',
        init: function(){
            var self = this;
            self.render();
        },
        render: function(evt, data){
            var self = this, 
                el,
                data = { BlogType: self.model.feed() };
            $.extend( data, self.tmplData );
            console.log(data);
            $.tmpl('livedesk>blogtype/blogtype', data, function(e,o){
                self.setElement(o);
                $(self.el).on(self.getEvent('click')+'test', 'h3', function(){
                        var li = $(this).parent().parent();
                        li.find('.blogtype-content').toggle(300);
                        li.toggleClass("collapse-open");
                });
                self.postPosts = new PostPostsView({
                    el: $('<div></div>').appendTo(self.el.find('.blogtype-content')),
                    collection: self.model.get('PostPosts')
                });
            });
        }
    });
});