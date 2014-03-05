define([ 
    'providers', 
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'action'),
    config.guiJs('livedesk', 'views/post'),
    config.guiJs('livedesk', 'views/statuses'),
    config.guiJs('livedesk', 'views/user-verification'),
    config.guiJs('livedesk', 'views/user-filter'),
    config.guiJs('livedesk', 'models/sync'),
    config.guiJs('livedesk', 'models/sync-collection'),
	'jqueryui/draggable',
	'jqueryui/autocomplete',
    'providers/chain/adaptor',
    config.guiJs('livedesk', 'models/blog'),
    config.guiJs('livedesk', 'models/posts'),
    config.guiJs('livedesk', 'models/users'),
    config.guiJs('livedesk', 'models/autoposts'),
	config.guiJs('livedesk', 'models/autochainposts'),
	config.guiJs('livedesk', 'models/autodeleteposts'),
	config.guiJs('livedesk', 'models/source'),
	config.guiJs('livedesk', 'models/sources'),
	config.guiJs('livedesk', 'models/autocollection'),
	config.guiJs('livedesk', 'models/postdeleted'),
    'tmpl!livedesk>items/implementors/chain',
    'tmpl!livedesk>providers/chain',
	'tmpl!livedesk>providers/chain/blogs',
	'tmpl!livedesk>providers/chain/blog-link',
	'tmpl!livedesk>providers/chain/blog-content',
	'tmpl!livedesk>providers/chain/hidden-blog-content',
	'tmpl!livedesk>providers/chain/timeline',
	'tmpl!livedesk>citizen-desk/statuses-list',
	'tmpl!livedesk>citizen-desk/statuses-filter-list',
	'tmpl!livedesk>citizen-desk/checker-list',
	'tmpl!livedesk>citizen-desk/chain-checker-list'
], function(
		providers,
		$,
		Gizmo,
		BlogAction,
		PostView,
		StatusesView,
		UserVerification,
		UserFilter,
		SyncModel,
		SyncCollection
	) {
	
    var PostStatusesView = StatusesView.extend({
    		template: 'livedesk>citizen-desk/statuses-list'
	    }),
	    StatusesFilterView = StatusesView.extend({
			template: 'livedesk>citizen-desk/statuses-filter-list'  	
	    }),
		autoSources = Gizmo.Auth(new SyncCollection()),
    	ChainPostView = PostView.extend({
    		events: {
    			'': { afterRender: 'addElements', mouseleave: 'killMenu'},
    			'[data-status-key]': { click: 'changeStatus'},
    			'[data-action="hide"]': { click: 'hide' },
    			'[data-action="unhide"]': { click: 'unhide' }
    		},
    		changeStatus: function(evt){
    			var self = this,
    				status = $(evt.target).closest( "li" ).attr('data-status-key');
    			self.model.changeStatus(status);
    		},
    		hide: function(evt){
    			evt.preventDefault();
    			var self = this;
    			self.model.hide().done(function(){
    				self._parent.removeModel(self.model);
    				self.el.remove();
    			});
    		},
    		unhide: function(evt){
				evt.preventDefault();
				var self = this;
				self.model.unhide().done(function(){
					self._parent.removeModel(self.model);
					self.el.remove();
				});
    		},
    		addElements: function() {
    			var self = this;
    			self.addDraggable();
    			self.addUserVerification();
    		},
    		killMenu: function(evt) {
				var self = this;
    			//self.userVerification.killMenu();
    			$('.dropdown.open .dropdown-toggle', self.el).dropdown('toggle');
    		},
			addUserVerification: function(){
				var self = this;
				self.userVerification = new UserVerification({ 
					el: $('.verification-assign',self.el),
					post: self.model
				});
			},
    		addDraggable: function(){
				var self = this, obj;
				self.el.draggable({
					handle: '.drag-bar',
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
					    $(this).data('post', self.model );
					}
				});
    		}
    	}),
		TimelineView = Gizmo.View.extend({

			xfilter:
                'PublishedOn, DeletedOn, Order, Id, CId, Content, CreatedOn, Type,'+
				'AuthorName, Author.Source.Name, Author.Name, Author.Source.Id, Author.Source.IsModifiable, IsModified, Author.User.*, '+
					'Meta, IsPublished, Creator.FullName, PostVerification.Status.Key, '+
					'PostVerification.Checker.Id, PostVerification.Checker.FullName, AuthorImage',
					//'PostVerification.Checker.Id, PostVerification.Checker.FirstName, PostVerification.Checker.LastName, PostVerification.Checker.Name'
			filter: { data : {}},
			init: function(){
				var self = this;
				self._views = [];
                self.collection.reset([]);
                self.collection.resetStats();
                self.filter.data = {thumbSize: 'medium', 'desc': 'order'};
				self.collection.keepPolling = function(){
					return self.el.is(":visible");
				}
				//self.collection.modelDataBuild = function(model){ return model;};
				self.collection
					.on('read readauto', function(evt)
					{
						self.render();
						self.toggleMoreVisibility();
					})
					.on('addingsauto update', function(evt, data)
					{
						self.addAll(evt, data);
						self.toggleMoreVisibility();
					})
					.on('removeingsauto', self.removeAll, self)
					.desc('order')
					.on('read update readauto updateauto', function(){
						$('.postlist-container',self.el).show();
						$('.chainblogs',self.el).show();
					})
					.limit(self.collection._stats.limit)
					.xfilter(self.xfilter);
			},
			toggleMoreVisibility: function()
			{
				var self = this;
				if( (self.collection._stats.offset >= self.collection._stats.total) || self.collection.search) {
					$('#more-chain', self._parent.el).hide();
				}
			},

			more: function(evnt, ui)
			{
				this.collection
					.xfilter(this.xfilter)
					.limit(this.collection._stats.limit)
					.offset(this.collection._stats.offset)
					.desc('order')
					.sync();
			},
			activate: function(data){			
				data = data || {};
				var self = this;
			    
			    self.filter.data = $.extend(self.filter.data, data);
				self.collection.resetStats();
				self.collection
					.limit(self.collection._stats.limit)
					.auto({
						headers: { 'X-Filter': self.xfilter },
                        data: self.filter.data
					});
			},
			deactivate: function(){
					$('.postlist-container',this.el).hide();
					$('.chainblogs',this.el).hide();
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
	            $('.postlist-container').css({'top': top_space});
			},
			removeModel: function(model) {
				this.collection.remove(model.hash());
			},
			removeOne: function(view) {
				var 
					self = this,
					pos = self._views.indexOf(view);
				if(pos !== -1 ) {
					self._views.splice(pos,1);
				}
			},
			removeAll: function(evt, data)
			{
				var self = this;
				for( var i = 0, count = data.length; i < count; i++ ) {
					if(data[i].chainView) {
						data[i].chainView.remove();
						delete data[i].chainView;
					}
				}
			},
            findView: function(view) {
                for (var i = 0, length = this._views.length; i < length; i++) {
                    if (view.model.href === this._views[i].model.href) {
                        return i;
                    }
                }

                return -1;
            },

			/*!
			 * Order given view in timeline
			 * If the view is the first one the it's added after #load-more selector
			 * returns the given view.
			 */
			orderOne: function(view) {
				var pos = this.findView(view);

				/*!
				 * View property order need to be set here
				 *   because could be multiple updates and 
				 *   orderOne only works for one update.
				 */
				view.order = parseFloat(view.model.get('Order'));

                // ignore deleted/unpublished posts
                if (isNaN(view.order)) {
                    if (pos > -1) {
                        this.views[pos].undelegateEvents();
                        this.views[pos].el.remove();
                        this._views.splice(pos, 1);
                    }

                    return;
                }

				/*!
				 * If the view isn't in the _views vector
				 *   add it.
				 */
				if (pos === -1) {
					this._views.push(view);
				}

				/*!
				 * Sort the _view vector descendent by view property order.
				 */
				this._views.sort(function(a,b) {
					return b.order - a.order;
				});

				pos = this.findView(view);
				if (pos === 0) {
					/*!
					 * If the view is the first one the it's added after #load-more selector.
					 *   else
					 *   Reposition the dom element before the old (postion 1) first element.
					 */
					if (this._views.length === 1) {
						this.el.find('.chainblogs').html(view.el);
					} else {
						view.el.insertBefore(this._views[1].el);
					}
				} else {
					/*!
					 * Reposition the dom element after the previous element.
					 */
					view.el.insertAfter(this._views[pos - 1].el);
				}

				return view;
			},
			addOne: function(model) {
				/*!
				 * @TODO: remove this when source it will be put on the blog children.
				 */
				var self = this,
					blog = this.blog.feed();
				if($.type(blog['EmbedConfig']) === 'string') {
					blog['EmbedConfig'] = $.parseJSON(blog['EmbedConfig']);
				}
				var chainView = new ChainPostView({ 
					_parent: this,
					model: model,
					blog: blog,
					tmplImplementor: 'implementors/chain'
				});
				model.chainView = chainView;
				this.orderOne(chainView);
			},
			addAll: function(evt, data){
				if(data) {
					for(var i = 0, count = data.length; i < count; i++) {
						this.addOne(data[i]);
					}
				}
			},
			clearCheckerFilter: function(checker) {
				delete this.collection.search;
				delete this.filter.data.checker;
			},
			filterChecker: function(checker) {
                var view = this;
                this.deactivate();
                this.collection.reset([]);
                this.collection.resetStats();
                this._views = [];
				if (checker.Id !== '') {
					this.collection.search = checker.Id;
					this.filter.data.checker = checker.Id;
                    this.collection.sync(this.filter);
				} else if (!autoSources.isAuto(this.sourceId)) { // reset after
					this.clearCheckerFilter(); 
                    this.collection
						.limit(this.collection._stats.limit)
						.offset(0)
						.desc('order')
                    this.activate();
				}
			},
			clearStatusFilter: function(){
				delete this.filter.data.status;
				delete this.collection.search;				
			},
			filterStatus: function(keyStatus) {
                var view = this;
                this.deactivate();
                this.collection.reset([]);
                this.collection.resetStats();
                this._views = [];
				if (keyStatus !== 'all') {
					this.collection.search = keyStatus;
					this.filter.data.status = keyStatus;
                    this.collection.sync(this.filter);
				} else if (!autoSources.isAuto(this.sourceId)) { // reset after
					this.clearStatusFilter();
                    this.collection
						.limit(this.collection._stats.limit)
						.offset(0)
						.desc('order')
                    this.activate();
				}
			},
			search: function(what) {
                var view = this;
                this.deactivate();
                this.collection.reset([]);
                this.collection.resetStats();
                this._views = [];
				if (what) {
					this.collection.search = what;
                    this.collection.sync({data: {search: what}});
				} else if (!autoSources.isAuto(this.sourceId)) { // reset after
					delete this.collection.search;
                    this.collection
						.limit(this.collection._stats.limit)
						.offset(0)
						.desc('order')
                    	//.sync();
                    this.activate();
				}
			}
		}),
		ChainBlogLinkView = Gizmo.View.extend({
			events: {
				'': { click: 'toggleActive'}
			},
			init: function() {
				//this.model.on('read update', this.render, this);
				this.render();
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
		HiddenChainBlogContentView = Gizmo.View.extend({
			init: function(){
				//this.render();
				this.model.hiddenChainBlogContentView = this;
			},
			deactivate: function() {
				this.active = false;
				this.timelineView.deactivate();
			},
			activate: function() {
				var self = this;
				self.active = true;
                var isAuto = autoSources.isAuto(self.model.sourceId);
                $('.autopublish input:checkbox').prop('checked', isAuto);
                $('.autopublish .sf-toggle-custom').toggleClass('sf-checked', isAuto);
                $('#automod-info').hide();
                if(self.timelineView) {
                	self.timelineView.activate({ isDeleted: 'True' });
            	} else {
            		self.render(function(){
            			self.timelineView.activate({ isDeleted: 'True' });
            		});
            	}
			},
			render: function(callback){
				var self = this,
					posts = self.model.get('PostSourceUnpublishedHidden');
				$.tmpl('livedesk>providers/chain/hidden-blog-content', { Blog: self.model.feed()}, function(e, o){
					self.setElement(o);
					self.timelineView = new TimelineView({ 
							_parent: self,
							el: self.el,
							collection: posts,
							sourceId: self.model.sourceId,
							sourceURI: self.model.href,
							blog: self._parent.blog
					});
					if(callback) 
						callback();
				});
			}
		}),
		ChainBlogContentView = Gizmo.View.extend({
			events: {
				'#more-chain': { click: 'more'}
			},
            more: function(evt) {
            	var self = this;
            	self.timelineView.more(evt);
            },
			init: function(){
				this.render();
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
                isAuto ? this.timelineView.deactivate() : this.timelineView.activate({ isDeleted: 'False' }); //, limit:  this.timelineView.collection._stats.limit
			},
			render: function(){
				var self = this,
					posts = Gizmo.Auth(self.model.get('PostSourceUnpublished'));
				//posts.param('False', 'isDeleted');
				$.tmpl('livedesk>providers/chain/blog-content', { Blog: self.model.feed()}, function(e, o){
					self.setElement(o);
					self.timelineView = new TimelineView({
							_parent: self,
							el: self.el,
							collection: posts,
							sourceId: self.model.sourceId,
							sourceURI: self.model.href,
							blog: self._parent.blog
					});
				});
			}
		}),
		ChainBlogsView = Gizmo.View.extend({
			events: {
				'.sf-searchbox a': {click: 'removeSearch'},
				'.sf-searchbox input': {keypress: 'checkEnter'},
                '.sf-toggle:checkbox': {change: 'toggleAutopublish'},
                '#hidden-toggle': { click: 'toggleHidden' },
                '[data-status-filter-key]': { click: 'filterStatus'},
			},
			init: function(){
				// userSearch = new UserSearch();
				// return;
				var self = this,
					href;
				self.chainBlogLinkViews = [];
				self.chainBlogContentViews = [];
				self.hiddenChainBlogContentViews = [];
				self.hiddenToggle = false;
				if($.type(self.sourceBlogs) === 'undefined') {
					self.sourceBlogs = Gizmo.Auth(new Gizmo.Register.Sources());
					/*!
					 * @TODO: remove this when source it will be put on the blog children.
					 */
					href = this.blog.get('Source').href;
					//add 'my' in the href only if it does not exists already
					var my = href.indexOf('/my/') != -1 ? '' : 'my/'
					href = href.replace(/LiveDesk\/Blog\/(\d+)\/Source\//, my + 'Data/SourceType/chained%20blog/Source?blogId=$1');
					self.sourceBlogs.setHref(href);
					self.sourceBlogs
						.on('read', this.render, this)
						.xfilter('Name,Id,PostSourceUnpublished')
						.sync();
				}
			
                autoSources.url = this.blog.get('Sync').href;
				
                var heads = autoSources.xfilter;
                heads["Authorization"] = localStorage.getItem('superdesk.login.session');
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
			filterStatus: function(evt){
				evt.preventDefault();
				$('[data-status-filter-key]', self.el).removeClass('active');
				var el = $(evt.target).closest('[data-status-filter-key]'),
					keyStatus = el.attr('data-status-filter-key'),
					active = this.getActiveView();
				el.addClass('active');
				if (active) {
					if(this.hiddenToggle)
						active.model.hiddenChainBlogContentView.timelineView.filterStatus(keyStatus);
					else
						active.model.chainBlogContentView.timelineView.filterStatus(keyStatus);
				}
			},
			filterChecker: function(checker) {
				var active = this.getActiveView();
				$('#chain-checker-name', this.el).text(checker.FullName)
				if (active) {
					if(this.hiddenToggle)
						active.model.hiddenChainBlogContentView.timelineView.filterChecker(checker);
					else
						active.model.chainBlogContentView.timelineView.filterChecker(checker);
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
				this.clearHidden();
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
                if($.type(self.blog.data.EmbedConfig) === 'string') {
                	self.blog.data.EmbedConfig = JSON.parse(self.blog.data.EmbedConfig)
                }
                var verificationStatus = self.blog.data.EmbedConfig && self.blog.data.EmbedConfig.VerificationToggle;
                $.tmpl('livedesk>providers/chain', {sourceBlogs: sourceBlogs, verificationStatus: verificationStatus }, function(e,o){
						$(self.el).html(o);
					var chainBlog,
						chainBlogLinkView,
						timelineCollection,
						$linkEl = self.el.find('.feed-info'),
						$contentEl = self.el.find('.chain-header'),
						blogParts = self.blog.href.match(/Blog\/(\d+)/);

					self.userFilter = new UserFilter({ 
						el: $('.filter-assign',self.el),
						template: 'livedesk>citizen-desk/chain-checker-list',
						_parent: self
					});
                    self.sourceBlogs.each(function(id,sourceBlog){
						// chainBlog = new Gizmo.Register.Blog();
						// chainBlog.defaults.PostUnpublished = Gizmo.Register.AutoPosts;
						// chainBlog.setHref(sourceBlog.get('URI').href);
						// chainBlog.sync();
						chainBlog = sourceBlog;
						timelineCollection = new Gizmo.Register.AutoChainPosts();
						timelineCollection.model.prototype.blogId = blogParts[1];
						timelineCollection.href = chainBlog.get('PostSourceUnpublished').href;
						timelineCollection.isCollectionDeleted = function(model) {
							return(model.get('IsPublished') === 'True' || model.get('DeletedOn'));
						}
						chainBlog.data['PostSourceUnpublished'] = timelineCollection;
						hiddenTimelineCollection = new Gizmo.Register.AutoDeletePosts();
						hiddenTimelineCollection.model.prototype.blogId = blogParts[1];
						hiddenTimelineCollection.href = chainBlog.get('PostSourceUnpublished').href;
						hiddenTimelineCollection.isCollectionDeleted = function(model) {
							return(model.get('IsPublished') === 'True' || !model.get('DeletedOn'));
						}
						chainBlog.data['PostSourceUnpublishedHidden'] = hiddenTimelineCollection;

						chainBlog.sourceId = sourceBlog.get('Id');

						chainBlogLinkView = new ChainBlogLinkView({ model: chainBlog, _parent: self });
						chainBlogContentView = new ChainBlogContentView({ model: chainBlog, _parent: self });
						hiddenBlogContentView = new HiddenChainBlogContentView({ model: chainBlog, _parent: self })
						self.chainBlogLinkViews.push(chainBlogLinkView);
						self.chainBlogContentViews.push(chainBlogContentView);
						self.hiddenChainBlogContentViews.push(hiddenBlogContentView);
                        $linkEl.prepend(chainBlogLinkView.el);
						chainBlogContentView.el.insertAfter($contentEl);
						hiddenBlogContentView.el.insertAfter($contentEl);
					});
				});
			},
			clearStatusFilter: function(){
				this.activeView.model.chainBlogContentView.timelineView.clearStatusFilter();
				$('[data-status-filter-key]', this.el).removeClass('active');
				$('[data-status-filter-key="all"]', this.el).addClass('active');
			},
			clearCheckerFilter: function(){
				this.activeView.model.chainBlogContentView.timelineView.clearCheckerFilter();
				$('#chain-checker-name').text(_('All Assigners'));
			},
			clearHidden: function(){
				var self = this,
					view = this.activeView,
					elem = $('#hidden-toggle', self.el),
					is_active = elem.hasClass('active');
				if (view) {
					if (is_active) {
						self.hiddenToggle = false;
						view.model.hiddenChainBlogContentView.deactivate();
					}
				}
				elem.removeClass('active');
			},
			toggleHidden: function(e) {
				e.preventDefault();
				var self = this,
					view = this.activeView,
					elem = $('#hidden-toggle', self.el),
					is_active = elem.hasClass('active');
				self.clearStatusFilter();
				self.clearCheckerFilter();
				if (view) {
					if (is_active) {
						self.hiddenToggle = false;
						//we want to go in normal view
						view.model.chainBlogContentView.activate();
						view.model.hiddenChainBlogContentView.deactivate();
					}
					else {
						//we want to go in deleted items view
						self.hiddenToggle = true;
						view.model.hiddenChainBlogContentView.activate();
						view.model.chainBlogContentView.deactivate();
					}
					elem.toggleClass('active');
				}
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
                    //CId = autoSources.getLastSyncId(view.model.sourceId);
                    if (sync) {
                        sync.save({Auto: autopublish ? 'True' : 'False'}, {patch: true}).done(function(){
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

	    var blog = Gizmo.Auth(new Gizmo.Register.Blog(blogUrl));
        blog.on('read', function() {
			chain = new ChainBlogsView({
				el: this.el, 
				blog: blog,
			});
		}.apply(this));
        blog.sync();
	}});

    return providers;
});
