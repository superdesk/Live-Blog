define([
	'jquery', 
    'gizmo/superdesk',
    'jquery/superdesk', 
    'jquery/rest', 
    'jqueryui/texteditor',
    'jquery/utils',
    config.guiJs('livedesk', 'models/languages'),
    config.guiJs('livedesk', 'models/blogtypes'),
	'tmpl!livedesk>add',
    'tmpl!livedesk>add/languages',
    'tmpl!livedesk>blogtypes',
    'tmpl!livedesk>blogtype/blogtype',
], function( $, Gizmo) {

    var 
    LanguagesView = Gizmo.View.extend({
        init: function(){
            var self = this;
            self.collection
                .on('read update', self.render, self)
                .xfilter('Id,Name')
                .sync();
        },
        render: function(evt, data){
            this.el.tmpl('livedesk>add/languages', { Languages: this.collection.feed() });
        }
    }),
    PostPostsView = Gizmo.View.extend({
        init: function(){
            var self = this;
            self.collection
                .on('read update', self.render, self)
                .xfilter('*')
                .sync();
        },
        render: function(evt, data){
            this.el.tmpl('livedesk>blogtype/postposts', { PostPosts: this.collection.feed() });
        }        
    }),
    BlogTypeView =  Gizmo.View.extend({
        el: 'li',
        init: function(){
            var self = this;
            self.render();
        },
        render: function(evt, data){
            var self = this;
            $.tmpl('livedesk>blogtype/blogtype', { BlogType: self.model.feed() }, function(e,o){
                self.setElement(o);
                self.postPosts = new PostPostsView({
                    el: self.el.find('.posttypes'),
                    collection: self.model.get('PostPosts')
                });
            });
        }
    }),
    BlogTypesView = Gizmo.View.extend({
        init: function(){
            var self = this;
            self.collection
                .on('read update', self.render, self)
                .xfilter('*')
                .sync();
        },
        addOne: function(model){
            var blogTypeView = new BlogTypeView({ model: model });
            this.el.find('.blogtype-list').prepend(blogTypeView.el)
        },
        addAll: function(evt, data) {
            data = (data === undefined) ? this.collection._list : data;
            for( var i = 0, count = data.length; i < count; i++ ){
                this.addOne(data[i]);
            }
        },
        render: function(evt, data){
            this.el.tmpl('livedesk>blogtypes');
            this.addAll(evt, data);
        }
    }),
    AddBlogView = Gizmo.View.extend({
        init: function() {

        },
        refresh: function() {
            var self = this;
            $.tmpl('livedesk>add', {}, function(e, o){
                self.setElement(o);
                self.languagesView = new LanguagesView({
                    collection: new Gizmo.Register.Languages(),
                    el: self.el.find('.languages'),
                    _parent: self
                });
                self.blogtypesView = new BlogTypesView({
                    collection: new Gizmo.Register.BlogTypes(),
                    el: self.el.find('.blogtypes'),
                    _parent: self
                });                 
                self.el.modal('show');
            });
        }
    }),
    addBlogView = new AddBlogView({
    });
    $('body').append(addBlogView.el);
    return function()
    {
        addBlogView.refresh();
    }
});