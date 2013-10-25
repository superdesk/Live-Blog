define([ 
    'providers', 
    'jquery', 
    'gizmo/superdesk',
    config.guiJs('livedesk', 'action'),
    config.guiJs('livedesk', 'views/post'),
    config.guiJs('livedesk', 'models/sync'),
    config.guiJs('livedesk', 'models/sync-collection'),
	'jqueryui/draggable',
	'jqueryui/autocomplete',
    'providers/chain/adaptor',
    config.guiJs('livedesk', 'models/blog'),
    config.guiJs('livedesk', 'models/posts'),
    config.guiJs('livedesk', 'models/users'),
    config.guiJs('livedesk', 'models/autoposts'),
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
	'tmpl!livedesk>citizen-desk/checker-list',
], function(providers, $, Gizmo, BlogAction, PostView, SyncModel, SyncCollection) {

    var autoSources = new SyncCollection();
    var StatusesView = Gizmo.View.extend({
    	init: function(){
			var self = this;
			// if(!self.collection) {
			// 	self.collection = Gizmo.Auth(new Gizmo.Register.Statuses());
			// }
			// self.collection
			// 	.on('read', self.render, self)
			// 	.xfilter('EMail,FirstName,LastName,FullName,Name')
			// 	.sync()
			self.data = [
				{ "Key": "nostatus", "Name": _("No status")},
				{ "Key": "verified", "Name": _("Verified")},
				{ "Key": "unverified", "Name": _("Unverified")},
				{ "Key": "onverification", "Name": _("On verification")}
			];
			self.render();
    	},
    	render: function(){
    		var self = this;
    		//self.data = self.collection.feed();
    		self.el.tmpl('livedesk>citizen-desk/statuses-list', self.data);
    	}
    });
    	var Users = Gizmo.Auth(new Gizmo.Register.Users());
    		Users
    			.xfilter('Id,EMail,FirstName,LastName,FullName,Name')
    			//.limit(1)
    			.sync();
    	var
    		UserVerification = Gizmo.View.extend({
			init: function(){
				var self = this;
				self.data = [];
				this.render();
			},
			events: {
				'.assignment-result-list li': { 'click': 'changeChecker' },
				'input': { 'click': 'stopPropagation' }
			},
			stopPropagation: function(evt){
				evt.stopImmediatePropagation();
			},
			killMenu: function(){
				var self = this;
				$('.dropdown.open .dropdown-toggle', self.el).dropdown('toggle');
			},
			sync: function() {
				if(!self.collection) {
					self.collection = Gizmo.Auth(new Gizmo.Register.Users());
				}
				self.collection
					.on('read', self.render, self)
					.xfilter('EMail,FirstName,LastName,FullName,Name')
					.sync()    			
			},
			changeChecker: function(evt){
				var self = this,
					item = $(evt.target).closest('li').data( "item.autocomplete");
				self.post.changeChecker(item.value);
			},
			render: function(evt, data){
				var self = this;
				self.collection.each(function(){
					self.data.push({label: this.get('FullName'), value: this.feed()});
				});
				self.el.tmpl('livedesk>citizen-desk/checker-list', self.post.feed(), function(){
					var autocomp = $('input',self.el).autocomplete({
						autoFocus: true,
						minLength: 0,
						appendTo: $('.assignment-result-list',self.el),
						source: self.data
					}).data( "autocomplete" );
					autocomp._renderItem = function( ul, item ) {
							return $( "<li></li>" )
								.data( "item.autocomplete", item )
								.append( '<figure class="avatar-small"></figure><span>'+ item.label+'</span>'  )
								.appendTo( ul );
					};
					autocomp._renderMenu = function( ul, items ) {
						var self = this;
						$.each( items, function( index, item ) {
							self._renderItem( ul, item );
						});
						$( ul ).removeClass('ui-autocomplete');
					};
				});
			}
		}),
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
    			var self = this;
    			self.model.hide();
    		},
    		unhide: function(evt){
    			var self = this;
    			self.model.unhide();
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
    				post: self.model,
    				collection: Users
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

			headers: {
                'X-Filter': 'PublishedOn, DeletedOn, Order, Id, CId, Content, CreatedOn, Type,'+
				'AuthorName, Author.Source.Name, Author.Name, Author.Source.Id, Author.Source.IsModifiable, IsModified, Author.User.*, '+
					'Meta, IsPublished, Creator.FullName, PostVerification.Status.Key, '+
					'PostVerification.Checker.Id, PostVerification.Checker.FullName'
					//'PostVerification.Checker.Id, PostVerification.Checker.FirstName, PostVerification.Checker.LastName, PostVerification.Checker.Name'
            },

			init: function(){
				this._views = [];
				this.collection
					.on('read readauto', this.render, this)
					.on('addingsauto', this.addAll, this)
					.on('removeingsauto', this.removeAll, this)
					.xfilter();
			},
			activate: function(data){			
				data = data || {};
				var self = this,
			    	data = $.extend(data, {thumbSize: 'medium'});
                // if (autoSources.isPaused(self.sourceId)) {
                //     data['cId.since'] = autoSources.getLastSyncId(this.sourceId);
                // }
				self.collection
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
					if(data[i].postview) {
						data[i].postview.remove();
						delete data[i].postview;
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
					blogParts = self.blog.href.match(/Blog\/(\d+)/),
					modelHref = model.href.replace(/Blog\/Post/,'Blog/'+blogParts[1]+'/Post');
				model.setHref(modelHref);
				model.data['href'] = modelHref;
				var postView = new ChainPostView({ 
					_parent: this,
					model: model,
					tmplImplementor: 'implementors/chain'
				});
				model.postview = postView;
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
                $('#automod-info').toggle(isAuto);
                if(self.timelineView) {
                	self ? self.timelineView.deactivate() : self.timelineView.activate({ isDeleted: 'True' });
            	} else {
            		self.render(function(){
            			self.timelineView.activate({ isDeleted: 'True' });
            		});
            	}
			},
			render: function(callback){
				var self = this,
					posts = self.model.get('PostSourceUnpublishedHidden');
				posts.model = Gizmo.Register.PostDeleted;
				//posts.param('True', 'isDeleted');
				$.tmpl('livedesk>providers/chain/hidden-blog-content', { Blog: self.model.feed()}, function(e, o){
					self.setElement(o);
					self.timelineView = new TimelineView({ 
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
                isAuto ? this.timelineView.deactivate() : this.timelineView.activate({ isDeleted: 'False' });
			},
			render: function(){
				var self = this,
					posts = self.model.get('PostSourceUnpublished');
				//posts.param('False', 'isDeleted');
				$.tmpl('livedesk>providers/chain/blog-content', { Blog: self.model.feed()}, function(e, o){
					self.setElement(o);
					self.timelineView = new TimelineView({ 
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
                '[data-active="false"]': { click: 'toggleHidden' },
				'[data-active="true"]': { click: 'toggleVisible' }
			},
			init: function(){
				// userSearch = new UserSearch();
				// return;
				var self = this,
					href;
				self.chainBlogLinkViews = [];
				self.chainBlogContentViews = [];
				self.hiddenChainBlogContentViews = [];
				if($.type(self.sourceBlogs) === 'undefined') {
					self.sourceBlogs = new Gizmo.Register.Sources();
					/*!
					 * @TODO: remove this when source it will be put on the blog children.
					 */
					href = this.blog.get('Source').href;
					href = href.replace(/LiveDesk\/Blog\/(\d+)\/Source\//,'Data/SourceType/chained%20blog/Source?blogId=$1');
					self.sourceBlogs.setHref(href);
					self.sourceBlogs
						.on('read', this.render, this)
						.xfilter('Name,Id,PostSourceUnpublished')
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
						timelineCollection,
						$linkEl = self.el.find('.feed-info'),
						$contentEl = self.el.find('.chain-header');

                    self.sourceBlogs.each(function(id,sourceBlog){
						// chainBlog = new Gizmo.Register.Blog();
						// chainBlog.defaults.PostUnpublished = Gizmo.Register.AutoPosts;
						// chainBlog.setHref(sourceBlog.get('URI').href);
						// chainBlog.sync();
						chainBlog = sourceBlog;
						timelineCollection = new Gizmo.Register.AutoPosts();
						timelineCollection.href = chainBlog.get('PostSourceUnpublished').href;
						timelineCollection.isCollectionDeleted = function(model) {
							return(model.get('IsPublished') === 'True' || model.get('DeletedOn'));
						}
						chainBlog.data['PostSourceUnpublished'] = timelineCollection;
						hiddenTimelineCollection = new Gizmo.Register.AutoPosts();
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
			toggleHidden: function(e) {
				e.preventDefault();
				var self = this,
					view = this.activeView;
					//$(this).css('background-color', '#f2f2f2');
				if (view) {
					$('[data-active="false"]', self.el).addClass('hide');
					$('[data-active="true"]', self.el).removeClass('hide');
					view.model.hiddenChainBlogContentView.activate();
					view.model.chainBlogContentView.deactivate();
				}
			},
			toggleVisible: function(e) {
				e.preventDefault();
				var self = this,
					view = this.activeView;
				//$(this).css('background-color', '#DDDDDD');
				if (view) {
					$('[data-active="false"]', self.el).removeClass('hide');
					$('[data-active="true"]', self.el).addClass('hide');
					view.model.chainBlogContentView.activate();
					view.model.hiddenChainBlogContentView.deactivate();
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

	    var blog = new Gizmo.Auth(new Gizmo.Register.Blog(blogUrl));
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
