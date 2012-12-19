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
    'tmpl!livedesk>blogtype/postposts',
    'tmpl!livedesk>blogtype/add-window',
    'tmpl!livedesk>blogtype/add'
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
            var self = this;
            $.tmpl('livedesk>blogtype/postposts', { PostPosts: this.collection.feed() }, function(e, o){
                self.setElement(o);
            });
        }        
    }),
    BlogTypeView =  Gizmo.View.extend({
        el: 'li',
        namespace: 'livedesk',
        init: function(){
            var self = this;
            self.render();
        },
        render: function(evt, data){
            var self = this, el;
            $.tmpl('livedesk>blogtype/blogtype', { BlogType: self.model.feed() }, function(e,o){
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
    }),
    BlogTypesView = Gizmo.View.extend({
        init: function(){
            var self = this;
            self.collection
                .on('read update', self.render, self)
                .xfilter('Id,Name,PostPosts')
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
    BlogView = Gizmo.View.extend({
        init: function() {

        },
        refresh: function() {
            var self = this;
            $.tmpl('livedesk>add', {}, function(e, o){
                self.setElement(o);
                self.languagesView = new LanguagesView({
                    collection: self.languages,
                    el: self.el.find('.languages'),
                    _parent: self
                });
                self.blogtypesView = new BlogTypesView({
                    el: self.el.find('.blogtypes'),
                    collection: self.blogTypes,
                    _parent: self
                });                 
                self.el.modal('show');
            });
        }
    }),
    Add = {
        BlogTypeView: Gizmo.View.extend({
                events: {
                    '#save-add-blogtype': { 'click': 'save' }
                },
                pendingPosts: [],
                init: function() {
                    this.render();
                },
                render: function(){
                    var self = this;
                    $.tmpl('livedesk>blogtype/add',{}, function(e,o){
                        self.setElement(o);
                    });
                    return this;
                },
                save: function(){
                    var name = this.el.find('[name="blogtypename"]').val();
                    this.collection.insert({ Name: name });
                }
            })
    },
    Config = {
        BlogTypeView: Gizmo.View.extend({
            init: function(){
                var self = this;
                if(!self.model)
                    self.model = new Gizmo.Register.BlogType()
                this.render();
            },
            render: function(){

            }
        }),
        PostPostsView: Gizmo.View.extend({
            ini: function(){}
        })   
    },
    blogTypes = new Gizmo.Register.BlogTypes(),
    languages = new Gizmo.Register.Languages(),
    blogView = new BlogView({ blogTypes: blogTypes, languages: languages }),
    addBlogView = new Add.BlogTypeView({ collection: blogTypes });
    $('body')
        .append(blogView.el)
        .append(addBlogView.el);
    return function()
    {
        blogView.refresh();
    }
});