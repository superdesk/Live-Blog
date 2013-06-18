 define([ 
    'providers', 
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'action'),
    config.guiJs('livedesk', 'views/post'),
    config.guiJs('livedesk', 'models/sync'),
    config.guiJs('livedesk', 'models/sync-collection'),
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
], function(providers, $, Gizmo, BlogAction, PostView, SyncModel, SyncCollection) {

    var autoSources = new SyncCollection();

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
					    $(this).data('data', providers.chain.adaptor.universal(self.model, { Id: self._parent.sourceId, URI: self._parent.sourceURI } ));
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
			    var data = {thumbSize: 'medium'};
                if (autoSources.isPaused(this.sourceId)) {
                    data['cId.since'] = autoSources.getLastSyncId(this.sourceId);
                }

				this.collection
					.on('read update readauto updateauto', function(){
						self.el.find('.chainblogs').show();
					})
					.auto({
						headers: { 'X-Filter': 'PublishedOn, DeletedOn, Order, Id, CId, Content, CreatedOn, Type,'+
								'AuthorName, Author.Source.Name, Author.Name, Author.Source.Id, Author.Source.IsModifiable, IsModified, Author.User.*, '+
							  	'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id, Meta, IsPublished, Creator.FullName' },
                        data: data
					});
			},
			deactivate: function(){
				this.el.find('.chainblogs').hide();
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
				'': { click: 'toggleActive'}
			},
			init: function() {
				this.model.on('read update', this.render, this);
			},
            
            toggleActive: function(e) {
                if (this.el.hasClass('active')) {
                    this.deactivate(e);
                } else {
                    this.activate(e);
                }
            },

			deactivate: function(e) {
				if(e) e.stopPropagation();
				this.el.removeClass('active');
				this.model.chainBlogContentView.deactivate();
			},

			activate: function() {
				this.active = true;
				this.model.chainBlogContentView.activate();
				this._parent.setActive(this);
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
                var isAuto = autoSources.isAuto(this.model.sourceId);
                $('.autopublish input:checkbox').prop('checked', isAuto);
                $('.autopublish .sf-toggle-custom').toggleClass('sf-checked', isAuto);
                $('#automod-info').toggle(isAuto);
                isAuto ? this.timelineView.deactivate() : this.timelineView.activate();
			},
			render: function(){
				var self = this;
				$.tmpl('livedesk>providers/chain/blog-content', { Blog: self.model.feed()}, function(e, o){
					self.setElement(o);
					self.timelineView = new TimelineView({ 
							el: self.el,
							collection: self.model.get('PostPublished'),
							sourceId: self.model.sourceId,
							sourceURI: self.model.href
					});
				});
			}
		}),
		ChainBlogsView = Gizmo.View.extend({
			events: {
				'.sf-searchbox a': { click: 'removeSearch'},
				'.sf-searchbox input': { keypress: 'checkEnter'},
                '.sf-toggle:checkbox': {change: 'toggleAutopublish'}
			},
			init: function(){
				var self = this;
				self.chainBlogLinkViews = [];
				self.chainBlogContentViews = [];
				if($.type(self.sourceBlogs) === 'undefined') {
					self.sourceBlogs = new Gizmo.Register.Sources();
					self.sourceBlogs.setHref(this.blog.get('Source').href);
					self.sourceBlogs
						.on('read', this.render, this)
						.xfilter('URI,Name,Id')
						.sync();
				}

                autoSources.url = this.blog.get('Sync').href;
                autoSources.fetch({headers: autoSources.xfilter, reset: true});
			},

            getActiveView: function() {
                if (this.activeView) {
                    return this.activeView;
                }
            },

			search: function(what){
                var active = this.getActiveView();
                if (active) {
					active.model.chainBlogContentView.timelineView.search(what);
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
			setActive: function(view) {
                this.activeView = view;
				for (var i = 0; i < this.chainBlogLinkViews.length; i++) {
					if (this.chainBlogLinkViews[i] !== this.activeView) {
						this.chainBlogLinkViews[i].deactivate();
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
						chainBlog.setHref(sourceBlog.get('URI').href);
						chainBlog.sync();
                        chainBlog.sourceId = sourceBlog.get('Id');
						chainBlogLinkView = new ChainBlogLinkView({ model: chainBlog, _parent: self });
						chainBlogContentView = new ChainBlogContentView({ model: chainBlog, _parent: self });
						self.chainBlogLinkViews.push(chainBlogLinkView);
						self.chainBlogContentViews.push(chainBlogContentView);
						$linkEl.prepend(chainBlogLinkView.el);
						chainBlogContentView.el.insertAfter($contentEl);
					});
				});
			},

            toggleAutopublish: function(e) {
                e.preventDefault();
                var autopublish = $(e.target).is(':checked'),
                	view = this.activeView,
                	CId,
                	sync,
                	ret;
                if (view) {
                    sync = autoSources.findSource(view.model.sourceId);
                    CId = autoSources.getLastSyncId(view.model.sourceId);
                    if (sync) {
                        sync.save({Auto: autopublish ? 'True' : 'False', CId: CId}, {patch: true}).done(function(){
                        	view.model.chainBlogContentView.activate();
                        });
                    } else {
                        model = autoSources.create({
                        	Blog: this.blog.get('Id'),
                        	Source: view.model.sourceId,
                        	Auto: autopublish ? 'True' : 'False',
                        	Creator: localStorage.getItem('superdesk.login.id')
                        }, { 
                        	wait: true, 
                        	headers: autoSources.xfilter,
                        	success: function(){
								view.model.chainBlogContentView.activate();
                        	}
                        });
                    }
                }
            }
		});

	$.extend( providers.chain, { init: function(blogUrl) {
		this.adaptor._parent = this;
		this.adaptor.init();

	    var blog = new Gizmo.Auth(new Gizmo.Register.Blog(blogUrl));
        blog.on('read', function() {
			chain = new ChainBlogsView({el: this.el, blog: blog});
		}.apply(this));
        blog.sync();
	}});

    return providers;
});
