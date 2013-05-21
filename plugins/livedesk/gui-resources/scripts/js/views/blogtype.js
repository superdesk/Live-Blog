 define([
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'views/postposts'), 

    'tmpl!livedesk>blogtype/blogtype',
    'tmpl!livedesk>blogtype/delete-blogtype-modal',
], function( $, Gizmo, PostPostsView ) {
    if(!$('#delete-blogtype').length) {
        $.tmpl('livedesk>blogtype/delete-blogtype-modal', {}, function(e,o){
            $('body').append(o);
        });
    }
   return Gizmo.View.extend({
        tmplData: {},
        tagName: 'li',
        namespace: 'livedesk',
        events: {
            '[name="remove-blogtype"]': { 'click': 'removeBlogTypeDialog' },
            '[name="edit-blogtype"]': { 'click': 'editBlogType' }
        },
        init: function(){
            var self = this;
            self.model.on('delete', self.remove, self);
            self.render();
        },
        editBlogType: function(evt) {
            evt.preventDefault();
            var self = this;
            self._parent.configBlogType.model = self.model;
            self._parent.configBlogType.render();
            self._parent.configBlogType.el.find('#add-blogtype').modal('show');
        },
        remove: function(evt){
            evt.preventDefault();
            this.el.remove();
        },
        removeBlogTypeDialog: function() {
            var self = this;
            $('#delete-blogtype #blogtype-name').text(self.model.get('Name'));
            $('#delete-blogtype .yes')
                .off(this.getEvent('click'))
                .on(this.getEvent('click'), function(){
                    self.model.remove().sync();
                });
        },
        render: function(evt, data){
            var self = this, 
                el,
                data = { BlogType: self.model.feed() };
            $.extend( data, self.tmplData );
            $.tmpl('livedesk>blogtype/blogtype', data, function(e,o){
                self.setElement(o);
                $(self.el).on(self.getEvent('click')+'test', 'h3', function(){
                        var li = $(this).parent().parent();
                        li.find('.blogtype-content').toggle(300);
                        li.toggleClass("collapse-open");
                });
                self.postPosts = new PostPostsView({
                    el: $('<div></div>').appendTo(self.el.find('.blogtype-content')),
                    collection: self.model.get('Post')
                });
            });
        }
    });
});