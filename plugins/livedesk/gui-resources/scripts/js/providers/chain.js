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
					    $(this).data('data', providers.chain.adaptor.universal(self.model));
					}
				});
    		}
    	}),
		TimelineView = Gizmo.View.extend({
			init: function(){
				this._views = [];
				this.collection
					.on('read readauto', this.render, this)
					.on('addingsauto', this.addAll, this)
					.xfilter();
			},
			activate: function(){
				var self = this;
				this.collection
					.on('read update readauto updateauto', function(){
						self.el.find('.chainblogs').show();
					})
					.auto({
						headers: { 'X-Filter': 'PublishedOn, DeletedOn, Order, Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Name, Author.Source.Id, IsModified, ' +
							   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id, Meta, IsPublished, Creator.FullName' },
						data: { thumbSize: 'medium'}
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
                    this.deactivate();
                } else {
                    this.activate();
                }
            },

			deactivate: function() {
                if (this.model.chainBlogContentView.active) {
				    this.model.chainBlogContentView.deactivate();
                    this._parent.setActive(null);
                }
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
				this.timelineView.activate();

                var isAuto = autoSources.isAuto(this.model.sourceId);
                $('.autopublish input:checkbox').prop('checked', isAuto);
                $('.autopublish .sf-toggle-custom').toggleClass('sf-checked', isAuto);
                $('#automod-info').toggle(isAuto);
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
                var autopublish = $(e.target).is(':checked');
                var view = this.activeView;
                if (view) {
                    sync = autoSources.findSource(view.model.sourceId);
                    if (sync) {
                        sync.save({Auto: autopublish ? 'True' : 'False'}, {patch: true});
                    } else {
                        autoSources.create({Blog: this.blog.get('Id'), Source: view.model.sourceId, Auto: autopublish ? 'True' : 'False'}, {headers: autoSources.xfilter});
                    }
                }

                $('#automod-info').toggle(autopublish);
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
