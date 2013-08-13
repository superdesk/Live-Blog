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

			headers: {
                'X-Filter': 'PublishedOn, DeletedOn, Order, Id, CId, Content, CreatedOn, Type,'+
				'AuthorName, Author.Source.Name, Author.Name, Author.Source.Id, Author.Source.IsModifiable, IsModified, Author.User.*, '+
					'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id, Meta, IsPublished, Creator.FullName'
            },

			init: function(){
				this._views = [];
				this.collection
					.on('read readauto', this.render, this)
					.on('addingsauto', this.addAll, this)
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
						headers: this.headers,
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
				//dynamically get size of header and set top space for list
	            var top_space = $('.chain-header').outerHeight() + 20;
	            $('.post-list.chainblogs').css({'top': top_space});
			},
			removeOne:function(view) {
				var 
					self = this,
					pos = self._views.indexOf(view);
				if(pos !== -1 ) {
					self._views.splice(pos,1);
				}
			},
			/*!
			 * Order given view in timeline
			 * If the view is the first one the it's added after #load-more selector
			 * returns the given view.
			 */
			orderOne: function(view) {
				var pos = this._views.indexOf(view);
				/*!
				 * View property order need to be set here
				 *   because could be multiple updates and 
				 *   orderOne only works for one update.
				 */
				view.order = parseFloat(view.model.get('Order'));
				/*!
				 * If the view isn't in the _views vector
				 *   add it.
				 */
				if ( pos === -1 ) {
					this._views.push(view);
				}
				/*!
				 * Sort the _view vector descendent by view property order.
				 */
				this._views.sort(function(a,b){
					return b.order - a.order;
				});
				/*!
				 * Search it again in find the new position.
				 */
				 for( var order = [], i = 0, count = this._views.length; i < count; i++ ){
				 	order.push(this._views[i].order);
				 }
				pos = this._views.indexOf(view);
				if( pos === 0 ){
					/*!
					 * If the view is the first one the it's added after #load-more selector.
					 *   else
					 *   Reposition the dom element before the old (postion 1) first element.
					 */
					if( this._views.length === 1) {
						this.el.find('.chainblogs').html(view.el);
					} else {
						view.el.insertBefore(this._views[1].el);
					}
				} else {
					/*!
					 * Reposition the dom element after the previous element.
					 */
					view.el.insertAfter(this._views[pos-1].el);
				}
				return view;
			},
			addOne: function(model) {
				var postView = new ChainPostView({ 
					_parent: this,
					model: model,
					tmplImplementor: 'implementors/chain'
				});
				this.orderOne(postView);
			},
			addAll: function(evt, data){
				for(var i = 0, count = data.length; i < count; i++) {
					this.addOne(data[i]);
				}
			},
			search: function(what) {
                var view = this;
                this.deactivate();
                this.collection.reset([]);
                this._views = [];
				if (what) {
                    this.collection.sync({data: {search: what}}).done(function() {
				        view.el.find('.chainblogs').show();
                    });
				} else if (!autoSources.isAuto(this.sourceId)) { // reset after
                    this.collection.sync();
                    this.activate();
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
				localStorage.setItem('selectedChainedBlog', this.model.get('Id'));
                this.active = true;
                this.model.chainBlogContentView.activate();
				this._parent.setActive(this);
			},

			render: function(){
				var self = this;
				$.tmpl('livedesk>providers/chain/blog-link', { Blog: self.model.feed(true)}, function(e,o) {
					self.setElement(o);
                    // small hack to select a chainbloglink as soon as its rendered.
                    // refactoring is needed, but until then this should work fine.
                    var selectedChainedBlog = localStorage.getItem('selectedChainedBlog');
                    if (selectedChainedBlog === self.model.get('Id') || selectedChainedBlog === null) {
                        setTimeout(function(){
                            self.activate();
                            self.el.addClass('active');
                        }, 100);
                    }
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
				'.sf-searchbox a': {click: 'removeSearch'},
				'.sf-searchbox input': {keypress: 'checkEnter'},
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
                evt.preventDefault();
				var input = $(evt.target).parents('.sf-searchbox').find('input');
					input.val('');
					this.search('');
                $(this.el).find('.sf-searchbox a').hide();
			},
			checkEnter: function(evt){
				if (evt.which == 13) {
				    this.search($(evt.target).val());
                }

                if ($(evt.target).val()) {
                    $(this.el).find('.sf-searchbox a').css('display', 'block');
                }
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
				var sourceBlogs = false;
                if (self.sourceBlogs._list.length > 0) {
                    sourceBlogs = true;
                }
                $.tmpl('livedesk>providers/chain', {sourceBlogs: sourceBlogs}, function(e,o){
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
