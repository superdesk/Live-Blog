 define([ 
    'providers', 
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'action'),
    config.guiJs('livedesk', 'views/post'),
	'jqueryui/draggable',
    'providers/chain/adaptor',
    config.guiJs('livedesk', 'models/blog'),
    config.guiJs('livedesk', 'models/posts'),
    config.guiJs('livedesk', 'models/autoposts'),
	config.guiJs('livedesk', 'models/source'),
	config.guiJs('livedesk', 'models/sources'),
	config.guiJs('livedesk', 'models/autocollection'),
    'tmpl!livedesk>items/implementors/chain',
    'tmpl!livedesk>providers/chain',
	'tmpl!livedesk>providers/chain/blogs',
	'tmpl!livedesk>providers/chain/blog-link',
	'tmpl!livedesk>providers/chain/blog-content',
	'tmpl!livedesk>providers/chain/timeline',
], function(providers, $, Gizmo, BlogAction, PostView) {
    var 
    	ChainPostView = PostView.extend({
    		events: {
    			'': { afterRender: 'addDraggable'}
    		},
    		addDraggable: function(){
				var self = this, obj;
				self.el.draggable({
					scroll: true,
					addClasses: false,
					revert: 'invalid',
					helper: 'clone',
					appendTo: 'body',
					zIndex: 2700,
					clone: true,
					start: function(evt, ui) {
					    item = $(evt.currentTarget);
					    $(ui.helper).css('width', item.width());
					    $(this).data('data', providers.chain.adaptor.universal(self.model));
					}
				});
    		}
    	}),
		TimelineView = Gizmo.View.extend({
			init: function(){
				this.collection
					.on('read readauto', this.render, this)
					.on('update updateauto', this.addAll, this)
					.xfilter();
			},
			activate: function(){
				var self = this;
				this.collection
					.on('read update readauto updateauto', function(){
						self.el.find('.chainblogs').css('display','block');
					})
					.auto({
						headers: { 'X-Filter': 'PublishedOn, DeletedOn, Order, Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Name, Author.Source.Id, IsModified, ' +
							   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id, Meta, IsPublished, Creator.FullName' },
						data: { thumbSize: 'medium'}
					});
			},
			deactivate: function(){
				this.el.find('.chainblogs').css('display','none');
				this.collection.stop();
			},
			render: function(evt){
				var self = this;
				$.tmpl('livedesk>providers/chain/timeline', {}, function(e, o){
					self.el.html(o);
					self.addAll(evt, self.collection._list);
				});
			},
			addOne: function(model) {
				var postView = new ChainPostView({ 
					model: model,
					tmplImplementor: 'implementors/chain'
				});
				this.el.find('.chainblogs').append(postView.el);
			},
			addAll: function(evt, data){
				for(var i = data.length-1; i > 0; i--) {
					this.addOne(data[i]);
				}
			},
			search: function(what) {
				var self = this;
				if( what !== '') {
					self.el.find('li').css('display','none');
					self.el.find("li:contains('"+what+"')").css('display','block');
				} else {
					self.el.find('li').css('display','block');
				}
			}
		}),
		ChainBlogLinkView = Gizmo.View.extend({
			events: {
				'': { click: 'activate'}
			},
			init: function(){
				this.model.on('read update', this.render, this);
			},
			deactivate: function() {
				this.el.removeClass('active');
				this.model.chainBlogContentView.deactivate();
			},
			activate: function() {
				this.active = true;
				this.model.chainBlogContentView.activate();
				this._parent.deactivateOthers(this);
			},
			render: function(){
				var self = this;
				$.tmpl('livedesk>providers/chain/blog-link', { Blog: self.model.feed(true)}, function(e,o) {
					self.setElement(o);
				});
			}
		}),
		ChainBlogContentView = Gizmo.View.extend({
			init: function(){
				this.model.on('read', this.render, this );
				this.model.chainBlogContentView = this;
			},
			deactivate: function() {
				this.active = false;
				this.timelineView.deactivate();
			},
			activate: function() {
				this.active = true;
				this.timelineView.activate();
			},
			render: function(){
				var self = this;
				$.tmpl('livedesk>providers/chain/blog-content', { Blog: self.model.feed()}, function(e, o){
					self.setElement(o);
					self.timelineView = new TimelineView({ 
							el: self.el, 
							collection: self.model.get('PostPublished') 
					});
				});
			}
		}),
		ChainBlogsView = Gizmo.View.extend({
			events: {
				'.sf-searchbox a': { click: 'removeSearch'},
				'.sf-searchbox input': { keypress: 'checkEnter'}
			},
			init: function(){
				var self = this;
				self.chainBlogLinkViews = [];
				self.chainBlogContentViews = [];
				if($.type(self.sourceBlogs) === 'undefined') {
					self.sourceBlogs = new Gizmo.Register.Sources;
					self.sourceBlogs.sync();
				}
				this.render();
			},
			search: function(what){
				var self = this;
				for(var i = 0, count = self.chainBlogContentViews.length; i < count; i++ ) {
					if(self.chainBlogContentViews[i].active) {
						self.chainBlogContentViews[i].timelineView.search(what);
						break;
					}
				}
			},
			removeSearch: function(evt){
				var input = $(evt.target).parents('.sf-searchbox').find('input');
					input.val('');
					this .search('');
			},
			checkEnter: function(evt){
				if(evt.which == 13) 
					this.search($(evt.target).val());
			},
			deactivateOthers: function(view) {
				var self = this;
				for(var i = 0, count = self.chainBlogLinkViews.length; i < count; i++ ) {
					if(self.chainBlogLinkViews[i] !== view) {
						self.chainBlogLinkViews[i].deactivate();
					}
				}
			},
			render: function() {
				var self = this;
				$.tmpl('livedesk>providers/chain', {}, function(e,o){
						$(self.el).html(o);
					var chainBlog,
						chainBlogLinkView,
						$linkEl = self.el.find('.feed-info'),
						$contentEl = self.el.find('.chain-header');
					
					self.sourceBlogs.each(function(id,sourceBlog){
						chainBlog = new Gizmo.Register.Blog();
						chainBlog.defaults.PostPublished = Gizmo.Register.AutoPosts;
						chainBlog.setHref(sourceBlog.get('URI'));
						chainBlog.sync();
						chainBlogLinkView = new ChainBlogLinkView({ model: chainBlog, _parent: self });
						chainBlogContentView = new ChainBlogContentView({ model: chainBlog, _parent: self });
						self.chainBlogLinkViews.push(chainBlogLinkView);
						self.chainBlogContentViews.push(chainBlogContentView);
						$linkEl.prepend(chainBlogLinkView.el);
						chainBlogContentView.el.insertAfter($contentEl);
					});
				});
			}
		})
	$.extend( providers.chain, { init: function(blogUrl) {
			this.adaptor._parent = this;
			this.adaptor.init();
			chain = new ChainBlogsView({ el: this.el, blogUrl: blogUrl });
		}
	});
    return providers;
});