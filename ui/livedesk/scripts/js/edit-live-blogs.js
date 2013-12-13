requirejs.config({
	paths: { 
		'providers': config.gui('livedesk/scripts/js/providers')
	}
});
define
([ 
    'providers/enabled', 
    'gizmo/superdesk',
    'jquery',
    config.guiJs('livedesk', 'action'),
    config.guiJs('media-archive', 'upload'),
    'router',
	'utils/extend',
    config.guiJs('livedesk', 'models/blog'),
	config.guiJs('livedesk', 'models/posttype'),
    config.guiJs('livedesk', 'models/post'),
	config.guiJs('livedesk', 'models/autocollection'),
    config.guiJs('livedesk', 'models/user'),
    config.guiJs('livedesk', 'models/new-collaborator'),
    'jquery/splitter', 'jquery/rest', 'jquery/param', 'jqueryui/droppable',
    'jqueryui/texteditor','jqueryui/sortable', 'jquery/utils', 
    config.guiJs('superdesk/user', 'jquery/avatar'),
    config.guiJs('livedesk', 'providers-templates'),
    'tmpl!livedesk>items/item',
    'tmpl!livedesk>items/implementors/timeline',
    'tmpl!livedesk>layouts/livedesk',
    'tmpl!livedesk>layouts/blog',
    'tmpl!core>layouts/footer',
    'tmpl!core>layouts/footer-static',
    'tmpl!core>layouts/footer-dinamic',
    'tmpl!livedesk>edit',
    'tmpl!livedesk>timeline-container',
	'tmpl!livedesk>timeline-action-item',
    'tmpl!livedesk>provider-content',
    'tmpl!livedesk>provider-link',
    'tmpl!livedesk>providers'
 ], 
function(providers, Gizmo, $, BlogAction, upload, router)
{
    /*!
     * Returns true if the data object is compose of only given keys
     */
	function isOnly(data, keys) 
	{
		if ($.type(keys) === 'string')
			keys = [keys];
		var count = 0, checkCount = keys.length;		
		for(i in data) {
			if( -1 === $.inArray(i, keys))
				return false;
			count++;	
			if( count>checkCount ) return false;
		};
		return (count === checkCount);
	}
		
		var h2ctrl = $.extend({}, $.ui.texteditor.prototype.plugins.controls),
		    timelinectrl = $.extend({}, $.ui.texteditor.prototype.plugins.controls),
		
		/*!
		 * Views for providers
		 * This one if for rendering of the content tab
		 */
		ProviderContentView =  Gizmo.View.extend
		({
			render: function()
			{
				var self = this,
				data = $.extend({},{link: this.name} , this.model);
				$.tmpl('livedesk>provider-content', data , function(err, out)
				{
						self.setElement( out );
						self.model.el = self.el;
				});
				return self;
			}
		}),
		
		/*!
		 * This rendering of the link tab, also has the event when showing the tab
		 */
		ProviderLinkView =  Gizmo.View.extend
		({
			events: 
			{
				"": {"show": "show"}
			},
			render: function()
			{
				var self = this,
				data = $.extend({},{link: this.name} , this.model);
				$.tmpl('livedesk>provider-link', data , function(err, out)
				{
						self.setElement( out );
				});
				return self;
			},
			show: function(evt)
			{
				// initialize the provider init method
				this.model.init(this.theBlog);
			}
		}),
		
		/*!
		 * This is the main view of the provider
		 * where is added the link tab view, content and the main html of the providers
		 */
		ProvidersView = Gizmo.View.extend
		({
			render: function() 
			{
				var self = this;
				$.tmpl('livedesk>providers', self.providers , function(err, out)
				{
					self.el.append( out );
					var links = self.el.find('ul:first'), contents = self.el.find('.tab-content:first');
					for( name in self.providers ) 
					{
						var provider = self.providers[name];
						var providerLinkView = new ProviderLinkView({ model: provider, name: name });
						
						providerLinkView.theBlog = self.theBlog;
						
						var providerContentView = new ProviderContentView({ model: provider, name: name });
						links.append(providerLinkView.render().el);
						contents.append(providerContentView.render().el);
					}
                                        $("[rel='tooltip']").tooltip();
				});
			}
		}),
		
		/*!
		 * 
		 */
		TimelineCollection = Gizmo.Register.AutoCollection.extend
		({
			model: Gizmo.Register.Post,
			href: new Gizmo.Url('/Post/Published'),
			parse: function(data) {
				if(data.total)
					if(data.offsetMore !== data.total) {
						this._stats.offsetMore = data.offsetMore;					
				}
				if(data.PostList)
					return data.PostList;
				return data;
			},
			isCollectionDeleted: function(model)
	        {
	        	var IsPublished = model.get('IsPublished') === 'True'?  true : false;
				if(!IsPublished) {
					delete model.data["PublishedOn"];
				}
	        	return !IsPublished;
	        }	
		}),
		
		/*!
		 * used for each item of the timeline
		 */
		PostView = Gizmo.View.extend
		({
			events: 
			{
				'': { sortstop: 'reorder' },
				'a.close': { click: 'removeDialog' },
				'a.unpublish': { click: 'unpublishDialog' },
				
				'.btn.cancel': {click: 'cancelActions', focusin: 'stopFocuseOut'},
				'.btn.publish': {click: 'save', focusin: 'stopFocuseOut'},
				'.editable': { focusin: 'edit'} //, focusout: 'focuseOut'}
			},
			showActions: function() {
				var self = this;
				self.el.find('.actions').removeClass('hide');
			},
			stopFocuseOut: function(evt) {
				var self = this,
					actions = self.el.find('.actions');
				actions.data('focuseout-stop',true);
			},
			focuseOut: function(evt) {
				var self = this,
					actions = self.el.find('.actions');
					setTimeout(function(){
						if(!actions.data('focuseout-stop')) {
							self.hideActions(evt, 1000);
						}
						actions.removeData('focuseout-stop');
					}, 100);
			},
			hideActions: function(evt, duration) {
				var self = this,
					actions = self.el.find('.actions'),
					duration = duration || 100;
				actions.fadeOut(duration, function(){
					self.el.find('.editable').html(function(){
						return $(this).data('previous');
					});
				});
			},
			cancelActions: function(evt) {
				this.stopFocuseOut(evt);
				this.hideActions(evt);
			},
			/*!
			 * subject to aop
			 */
			preData: $.noop,
			handleError: function(data) {
				var self = this;
				var status = data.status;
				var responseObj = jQuery.parseJSON( data.responseText );
				var responseText = responseObj.details.model.Post.Meta + _(' characters for text with HTML and formatting');
				switch ( status ) {
					case 400:
						self.showErrorMessage(responseText);
						break;
				}
			},
			showErrorMessage: function(responseText) {
				this.el.find('.message-error').html(responseText).css('display', 'inline');
			},
			save: function(evt)
			{
				var self = this,
					actions = self.el.find('.actions'),
					data = {
						Meta: this.model.get('Meta'),
						Content: $('.result-text.editable',this.el).html()
				};
				actions.data('focuseout-stop',true);
				if( !data.Content )
					delete data.Content;
				if($.type(data.Meta) === 'string')
					data.Meta = JSON.parse(data.Meta);
				data.Meta.annotation = { before: $('.annotation.top', self.el).html(), after: $('.annotation.bottom', self.el).html()};
				data.Meta = JSON.stringify(data.Meta);
				this.model.updater = this;

				// @FIX LB-814: Image post does allow comments to be added in a wrong place
				// @part 2
				if ('image' in self) {
					var separator = data.Content.length && data.Content[0] == "\n" ? '' : "\n";
					data.Content = self.image.wrap('<div>').parent().html() + separator + data.Content;
				}

				this.model.set(data).sync().done(function(){
					//handle done
				}).fail(function(data){
					//handle fail
					self.handleError(data);
				});

				this.el.find('.actions').stop().fadeOut(100, function(){
					$('.editable').removeData('previous');
				});
			},	
			edit: function(evt){
				var el = $(evt.target);
				this.el.find('.actions').stop(true).fadeTo(100, 1);
				if(!el.data('previous'))
					el.data('previous', el.html());
			},
			init: function()
			{
				var self = this;
				self.el.data('view', self);
				self.xfilter = 'DeletedOn, Order, Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Source.Id, Author.Source.IsModifiable, IsModified, ' +
								   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id, IsPublished, Creator.FullName';
				
				this.model
				    .on('delete', this.remove, this)
				    .off('unpublish').on('unpublish', function(evt) {
				    	//console.log('unpublish');
				    	self.remove(evt);
						 /*
						 * @TODO: remove this
						 * Dirty hack to actualize the owncollection
						 */
						var editposts = providers['edit'].collections.posts;
						editposts.xfilter(editposts._xfilter).sync();
				    }, this)
					.on('read', function()
					{
					    //console.log('read: ');
					    /*!
			             * conditionally handing over save functionallity to provider if
			             * model has source name in providers 
			             */
					    try
					    {
					        var src = this.get("Author").Source.Name;
	                        if( providers[src] && providers[src].timeline )
	                        {
	                            self.edit = providers[src].timeline.edit;
	                            self.save = providers[src].timeline.save;
	                        };
					    }
					    catch(e){ /*...*/ }
					    
						self.render();
					})
					.on('set', function(evt, data)
					{
						/*!
						 * If the set triggering is the edit provider then don't update the view;
						 */
						if(self.model.updater !== self) {
							self.rerender();
						}
					})
					.on('update', function(evt, data)
					{
						//console.log('update model: ',evt);
						/**
						 * Quickfix.
						 * @TODO: make the isCollectionDelete check in gizmo before triggering the update.
						 */
					    if( self._parent.collection.isCollectionDeleted(self.model) )
					    	return;
						/*!
						 * If the updater on the model is the current view don't update the view;
						 */
						if(self.model.updater === self) {
							delete self.model.updater; return;
						}
						/*!
						 * If the Change Id is received, then sync the hole model;
						 */						 
						if(isOnly(data, ['CId','Order'])) {
							self.model.xfilter(self.xfilter).sync();
						}
						else {
							self.rerender();
						}
						//; self.model.xfilter(xfilter).sync();
						
					})
					.xfilter(self.xfilter).sync({data: {thumbSize: 'medium', 'X-Format-DateTime': "yyyy-MM-ddTHH:mm:ss'Z'"}});
			},
			
			reorder: function(evt, ui)
			{
				var self = this, 
					next = $(ui.item).next('li'), 
					prev = $(ui.item).prev('li'), 
					id, 
					order, 
					newPrev = undefined, 
					newNext = undefined;
				if(next.length) {
					var nextView = next.data('view');
					nextView.prev = self;
					newNext = nextView;
					id = nextView.id;
					order = 'true';
				}
				if(prev.length){
					var prevView = prev.data('view');
					prevView.next = self;
					newPrev = prevView;
					id = prevView.id;
					order = 'false';
				}
				self.tightkNots();
				self.prev = newPrev;
				self.next = newNext;
				self.model.orderSync(id, order);
				self.model.ordering = self;
				self.model.xfilter(self.xfilter).sync().done(function(data){
					self.model.Class.triggerHandler('reorder', self.model);
				});
			},
			/**
			 * Method used to remake connection in the post list ( dubled linked list )
			 *   when the post is removed from that position
			 */			
			tightkNots: function()
			{
				if(this.next !== undefined) {
					this.next.prev = this.prev;
				}
				if(this.prev !== undefined) {
					this.prev.next = this.next;				
				}
			},
			
			rerender: function()
			{
				var self = this;
				self.el.fadeTo(500, '0.1', function(){
					self.render().el.fadeTo(500, '1');
				});
			},
			renderReorder: function()
			{
				var self = this, 
					order = parseFloat(self.model.get('Order'));
				if(isNaN(order)) {
					order = 0.0;
				}
				if ( !isNaN(self.order) && (order != self.order) && self.model.ordering !== self) {
					var actions = { prev: 'insertBefore', next: 'insertAfter' }, 
						ways = { prev: 1, next: -1}, 
						anti = { prev: 'next', next: 'prev'};
					for( var dir = (self.order - order > 0)? 'next': 'prev', cursor=self[dir];
						(cursor[dir] !== undefined) && ( cursor[dir].order*ways[dir] < order*ways[dir] );
						cursor = cursor[dir]
					);
					var other = cursor[dir];
					if(other !== undefined)
						other[anti[dir]] = self;
					cursor[dir] = self;
					self.tightkNots();
					self[dir] = other;
					self[anti[dir]] = cursor;
					self.el[actions[dir]](cursor.el);
				}
				if(this.model.ordering === self)
					delete this.model.ordering;
				self.order = order;
				self.id = this.model.get('Id');				
			}, 
			render: function()
			{
				var self = this,
					rendered = false,
					post = self.model.feed(true);

				self.renderReorder();
				if ( typeof post.Meta === 'string') {
					post.Meta = JSON.parse(post.Meta);
				}
				$.avatar.setImage(post, { needle: 'AuthorPerson.EMail', size: 36});
				$.tmpl('livedesk>items/item', { 
					Base: 'implementors/timeline',
					Post: post
				}, function(e, o) {
					self.setElement(o);
						BlogAction.get('modules.livedesk.blog-publish').done(function(action) {
							$('.editable', self.el).texteditor({plugins: {controls: timelinectrl}, floatingToolbar: 'top'});

							// @FIX LB-814: Image post does allow comments to be added in a wrong place
							if (self.model.data.Type.data.Key === 'image') {
								var editable = $('.editable', self.el);
								var image = $('a', editable);
								self.image = image.insertBefore(editable);
							}
						}).fail(function(action){
							self.el.find('.unpublish,.close').remove();
							if(self.model.get('Creator').Id == localStorage.getItem('superdesk.login.id'))
								self.el.find('.editable').texteditor({plugins: {controls: timelinectrl}, floatingToolbar: 'top'});
						});
				});
				return this;
			},	
			remove: function(evt)
			{
				//console.log('evt: ',evt);
				var self = this;
				/**
				 * @TODO remove only this view events from the model
				 */
				//self.model.off('delete unpublish read update set');
				self._parent.removeOne(self);
				self.tightkNots();
				$(this.el).fadeTo(500, '0.1', function(){
					self.el.remove();
				});
			},			
			removeDialog: function()
			{
				var self = this;
				$('#delete-post .yes')
					.off(this.getEvent('click'))
					.on(this.getEvent('click'), function(){
						self.model.removeSync();
					});

			},
			unpublishDialog: function(evt)
			{
				var self = this;
				$('#unpublish-post .yes')
					.off(this.getEvent('click'))
					.on(this.getEvent('click'), function(){
						self.model.unpublishSync();
					});

			}
		}),

		TimelineView = Gizmo.View.extend
		({
			stack: [],
			events: 
			{
				'ul.post-list': { sortstop: 'sortstop' },
				'#more': { click: 'more' }
			},
			moreHidden: false,
			init: function()
			{
				var self = this;
				self._views = [];
				self.moreHidden = false;
				self.collection.model.on('publish', function(evt, model){
					self.addOne(model);
				});
				self.xfilter = 'CId, Order, IsPublished';
				self.collection
					.on('read readauto', function(evt)
					{
						self.render();
						self.toggleMoreVisibility();
					})
					.on('addingsauto update', function(evt, data)
					{
						self.addAll(data);
						self.toggleMoreVisibility();
					})
					.on('removeingsauto', self.removeAllAutoupdate, self)
					.xfilter(self.xfilter)
					.limit(self.collection._stats.limit)
					.offset(self.collection._stats.offset)
					.desc('order');

				if (self._parent.model.isOpen()) {
					self.collection.auto();
				}

				self.collection.view = self;
				
				// default autorefresh on
				localStorage.setItem('superdesk.config.timeline.autorefresh', 1);
				// toggle autorefresh
				$('[data-toggle="autorefresh"]', self.uiCtrls).off('click')
				    .on('click', function(){ self.configAutorefresh.call(self, this); })
				    .tooltip({placement: 'bottom'});
				
			},
			toggleMoreVisibility: function()
			{
				var self = this;
				if(self.moreHidden)
					return;
				if(self.collection._stats.offset >= self.collection._stats.total) {
					self.moreHidden = true;
					$('#more', self._parent.el).hide();
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
			sortstop: function(evnt, ui)
			{
				$(ui.item).triggerHandler('sortstop', ui);
			},
			removeOne: function(view)
			{
				var 
					self = this,
					pos = self._views.indexOf(view);
				if(pos === -1)
					return self;
				//delete view.model.updater;
				self.total--;
				self._views.splice(pos,1);
				return self;
			},
			addOne: function(model)
			{	
				if (localStorage.getItem('superdesk.config.timeline.autorefresh') == 1) {
					if(model.postview && model.postview.checkElement()) {
						return;
					}
					var self = this,
						current = new PostView({model: model, _parent: self}),
						count = self._views.length;
					model.postview = current;
					current.order =  parseFloat(model.get('Order'));
					if(isNaN(current.order)) {
						current.order = 0.0;
					}
					if(!count) {
						this.el.find('ul.post-list').append(current.el);
						self._views = [current];
					} else {
						var next, prev;
						for(i=0; i<count; i++) {
							if(current.order>self._views[i].order) {
								prev = self._views[i];
								prevIndex = i;
							} else if(current.order<self._views[i].order) {
								next = self._views[i];
								nextIndex = i;
								break;
							}						
						}
						if(next) {
							current.el.insertAfter(next.el);
							next.prev = current;
							current.next = next;
							self._views.splice(nextIndex, 0, current);
							
						} else if(prev) {
							current.el.insertBefore(prev.el);
							prev.next = current;
							current.prev = prev;
							self._views.splice(prevIndex+1, 0, current);
						}				
					}
					$(current).on('render', function(){ self.autorefreshHandle.call(self, current.el.outerHeight(true)); });
				} else {
					this.stack.push(model);
				}
			},
			removeAllAutoupdate: function(evt, data)
			{
				/**
				 * @TODO: remove this
				 * Dirty hack to actualize the owncollection
				 */
				//console.log('removings: ',data);
				var editposts = providers['edit'].collections.posts;
				editposts.xfilter(editposts._xfilter).sync();
				var self = this;
				for( var i = 0, count = data.length; i < count; i++ ) {
					if(data[i].postview) {
						data[i].postview.remove();
						delete data[i].postview;
					}
				}
				//console.log('removings: ',data);
				//console.log('collection: ',this.collection._list);
			},
			addAll: function(data)
			{
				var i = data.length;
				while(i--) {
					this.addOne(data[i]);
				}
			},
			render: function()
			{
				
				var self = this;
				if($(':first',self.el).length == 0) {
					$.tmpl('livedesk>timeline-container', {}, function(e, o)
					{
						$(self.el).html(o)
							.find('ul.post-list')
							.sortable({ items: 'li',  axis: 'y', handle: '.drag-bar'} ); //:not([data-post-type="wrapup"])
						self.addAll(self.collection.getList());
					});
                }
			},
			
			/*!
			 * insert new post
			 */
			insert: function(data, view)
			{
				/*
			    var self = this,
			        post = Gizmo.Auth(new this.collection.model(data)),
			        syncAction = this.collection.insert(post);
			    
			    view && syncAction.done(function()
			    { 
			        var newView = new PostView({model: post, _parent: self});
			        newView.el.insertAfter(view.el);
			        view.el.remove();
			    });
				*/
				var self = this,
					post = Gizmo.Auth(new this.collection.model());
				delete data._parsed;
				post._new = true;
				post.set(data);
				this.collection.xfilter('CId,Order').insert(post).done(function(){
				    post.href = post.data.href;
				    
					self.collection.model.triggerHandler('publish', post);
					self.addOne(post);		
					if(view) {
						view.el.remove();
					}	
				}).fail(function(data){

					self.handleError(data, view);
				});
							
			},
			handleError: function(data, view) {
				var self = this;
				var status = data.status;
				var responseObj = jQuery.parseJSON( data.responseText );
				var responseText = responseObj.details.model.Post.Meta + _(' characters for text with HTML and formatting');

				switch ( status ) {
					case 400:
						$('.message-error', view.el).html(responseText).css('display', 'inline');
						break;
				}
			},
			publish: function(post)
			{
				if(post instanceof this.collection.model) 
					post.publishSync();
				else 
				{
					var model = new this.collection.model({ Id: data});
					
					this.collection.insert({});
					//model.publish();
				}
			},
			
			stoppedHeight: false,
			autorefreshHandle: function(newH)
			{
			    if (parseFloat(localStorage.getItem('superdesk.config.timeline.autorefresh'))) {
			    	return;
			    } else {
			    	var x = $('.live-blog-content').parents(':eq(0)').scrollTop();
			    	$('.live-blog-content').parents(':eq(0)').scrollTop( x + newH );
			    }
			},
			/*!
			 * configure autorefresh on timeline
			 * 0 is for no refresh
			 * 
			 */
			configAutorefresh: function(button)
            {
			    var cnfAuto = localStorage.getItem('superdesk.config.timeline.autorefresh');
	            if (!parseFloat(cnfAuto)) {
	                localStorage.setItem('superdesk.config.timeline.autorefresh', 1);
	                $(button).removeClass('active');
	                for (var i = 0; i < this.stack.length; i = i + 1) {
	                	this.addOne(this.stack[i]);
	                }
	                this.stack = [];
	            } else {
	                this.stoppedHeight = false;
	                localStorage.setItem('superdesk.config.timeline.autorefresh', 0);
	                $(button).addClass('active');
	            }
            }
		}),
		ActionsView = Gizmo.View.extend
		({
			events: {
				'[data-action="update"]': { "click": "update" }
			},
			init: function() {
				var self = this,
					PostTypes = Gizmo.Collection.extend({model: Gizmo.Register.PostType});
							
				self.collection = Gizmo.Auth(new PostTypes(self.theBlog+'/../../../../Data/PostType'));
				
				self.collection.on('read', function(){ self.render(); }).xfilter('Key').sync();				
			},
			render: function(){
				var self = this,
					PostTypes = this.collection.feed();
				this.el.tmpl('livedesk>timeline-action-item', { PostTypes: PostTypes }, function(){				
					var self = this;
				});
			},
			update: function(e) {
				var element = e.currentTarget;
				$('[data-info="filter"]').html($(element).html());
			}
		}),
		EditView = Gizmo.View.extend
		({
			timelineView: null,
			events: 
			{
				'[is-content] section header h2': { focusout: 'save' },
				'[is-content] #blog-intro' : { focusout: 'save' },
				'#toggle-status': { click: 'toggleStatus' },
				'#put-live .btn-primary': { click : 'putLive' },
				'#more': { click: 'more'},
				'#tabmove-down': { click: 'tabMoveDown'},
				'#tabmove-up': { click: 'tabMoveUp'}
			},
			more: function(evnt)
			{
				this.timelineView.more(evnt);
			},
			tabMoveDown: function(evt) {
				evt.preventDefault();
				var tabs = $(".side-tab-container .nav-tabs", this.el),
					top_pos = parseInt(tabs.css('top'));
				if ((top_pos + tabs.height()) > 90)
					tabs.css('top',top_pos-56+'px');
			},
			tabMoveUp: function(evt) {
				evt.preventDefault();
				var tabs = $(".side-tab-container .nav-tabs", this.el),
					top_pos = parseInt(tabs.css('top'));
				if (top_pos < 35) 
					tabs.css('top',top_pos+56+'px');				
			},
			responsiveTabs: function() {
				var cont = $(".side-tab-container", this.el),
					tabs = $(".side-tab-container .nav-tabs", this.el);
				if (cont.height() < tabs.height() ) {
					if (!cont.hasClass("compact-tabs")) {
						cont.addClass("compact-tabs");
						tabs.css('top','35px');
					}
				}
				else { 
					cont.removeClass("compact-tabs");
					tabs.css('top','0');
				}				
			},
			postInit: function()
			{
				var self = this;
				this.model = Gizmo.Auth(new Gizmo.Register.Blog(self.theBlog));
				
				this.model.xfilter('Creator.*').sync()
				    // once	
				    .done(function()
				    {
				        self.render();
				    });
			},
			/*
			 * TODO description
			 */
			drop: function(event, ui)
			{
				var self = this,
					data = ui.draggable.data('data'),
					post = ui.draggable.data('post'),
					
					either = data || post;
				if( either instanceof Gizmo.View)
				{
					either.parent = self.timelineView;
					either.render();
					$('ul.post-list', self.timelineView.el).prepend(either.el.addClass('first'));
					$('.editable', either.el).texteditor({plugins: {controls: h2ctrl}, floatingToolbar: 'top'});
				}
				else if(data !== undefined) {
					$.when(data).then(function(data) {
						if(data.NewUser && data.NewCollaborator) {
							var addCollaborator = function(sourceId, userId) {
									return Gizmo.Auth(new Gizmo.Register.NewCollaborator({
											Source: sourceId,
											User: userId
										})).xfilter('Collaborator.Id').sync();
								},
								user = Gizmo.Auth(new Gizmo.Register.User(data.NewUser));

							user.xfilter('User.Id')
								.sync()
									.done(function(dataUser){
										addCollaborator(data.NewCollaborator.Source,dataUser.Id)
											.done(function(dataCollaborator){
												delete data.NewUser;
												delete data.NewCollaborator;
												data.Author = dataCollaborator.Id;
												self.timelineView.insert(data);
											});
									}).fail(function(dataUser){
										console.log('Error: ',dataUser);
									});
						} else {
							self.timelineView.insert(data);
						}
					});
				}
				else if(post !== undefined)
				{
					self.timelineView.publish(post);
					// stupid bug in jqueryui you can make draggable desstroy
					setTimeout(function(){
						$(ui.draggable).removeClass('draggable').addClass('published').draggable("destroy");
					},1);
				}
			},
			/*!
             * Save description and title changes for the current model blog
             */
			save: function(evt)
			{
				var self = this;
				//console.log('evt: ',evt.type);
				BlogAction.get('modules.livedesk.blog-edit').done(function(action) {
					var content = $(self.el).find('[is-content]'),
					titleInput = content.find('section header h2'),
					descrInput = content.find('article#blog-intro'),
					data = {
							Title: $.styledNodeHtml(titleInput),
							Description: $.styledNodeHtml(descrInput)
					};
					self.model.set(data).sync().done(function() {
						content.find('.tool-box-top .update-success').removeClass('hide')
						setTimeout(function(){ content.find('.tool-box-top .update-success').addClass('hide'); }, 5000);
					})
					.fail(function() {
						content.find('.tool-box-top .update-error').removeClass('hide')
						setTimeout(function(){ content.find('.tool-box-top .update-error').addClass('hide'); }, 5000);
					});
				});
				
			},
			putLive: function()
			{
			    var self = this;
			    this.model.putLive().done(function()
                { 
                    var stsLive = $('[data-status="live"]', self.el);
                        stsOffline = $('[data-status="offline"]', self.el),
                        msgLive = $('#put-live-msg-live', self.el),
                        titleLive = $('#put-live-title-live', self.el),
                        msgOffline = $('#put-live-msg-offline', self.el),
                        titleOffline = $('#put-live-title-offline', self.el);
                    if( stsLive.hasClass('hide') )
                    {
                        stsLive.removeClass('hide');
                        stsOffline.addClass('hide');
                        msgLive.addClass('hide');
                        titleLive.addClass('hide');
                        msgOffline.removeClass('hide');
                        titleOffline.removeClass('hide');
                        return;
                    }
                    stsLive.addClass('hide');
                    stsOffline.removeClass('hide');
                    msgLive.removeClass('hide');
                    titleLive.removeClass('hide');
                    msgOffline.addClass('hide');
                    titleOffline.addClass('hide');
                });
			},
			textToggleStatus: function()
			{
				newText = this.model.get('ClosedOn')? _('Reopen blog'): _('Close blog');
				$(this.el).find('#toggle-status').text(newText+'');
			},
			/*!
             * Toggle ClosedOn field for the blog
             */			
			toggleStatus: function(e)
			{
				var self = this, now = new Date(),
					data = { ClosedOn:  (this.model.get('ClosedOn')? null: now.format('yyyy-mm-dd HH:MM:ss'))},
					content = $(this.el).find('[is-content]');
				this.model.set(data).sync().done(function() {
					content.find('.tool-box-top .update-success').removeClass('hide');
					setTimeout(function(){ content.find('.tool-box-top .update-success').addClass('hide'); }, 5000);
					router.reload();
				})
				.fail(function() {
					content.find('.tool-box-top .update-error').removeClass('hide')
					setTimeout(function(){ content.find('.tool-box-top .update-error').addClass('hide'); }, 5000);
				});
			},
			render: function()
			{
				var self = this,
                                // template data
                                //to do feed is not getting recursive read
				mfeed = this.model.feed(),
				embedConfig = {};
				if((mfeed.EmbedConfig !== undefined) && $.isString(mfeed.EmbedConfig))
					embedConfig = JSON.parse(mfeed.EmbedConfig);

				if(embedConfig.FrontendServer === undefined)
					embedConfig.FrontendServer = config.api_url;
				
				var
				data = $.extend({}, this.model.feed(), 
				{
                    BlogHref: self.theBlog,
                    BlogId: self.model.get('Id'),

					FooterDinamic: true,
					ui: 
					{
						content: 'is-content=1',
						side: 'is-side=1',
						submenu: 'is-submenu',
						submenuActive1: 'active'
					},
					OutputLink: embedConfig.FrontendServer,
					OutputLinkAlt: document.URL.split(':')[0] + embedConfig.FrontendServer,
				    isLive: function(chk, ctx){ return ctx.current().LiveOn ? "hide" : ""; },
				    isOffline: function(chk, ctx){ return ctx.current().LiveOn ? "" : "hide"; }
				});
                                var creator = this.model.get('Creator').feed();
                                $.extend(data, {'creatorName':creator.Name});
				$.superdesk.applyLayout('livedesk>edit', data, function()
				{
					BlogAction.get('modules.livedesk.blog-publish').done(function(action) {
						self.el.find('#role-blog-publish').show();
					});
					BlogAction.get('modules.livedesk.blog-publish').fail(function(action) {
						self.el.find('[data-target="configure-blog"]').css('display', 'none');
						self.el.find('[data-target="manage-collaborators-blog"]').css('display', 'none');
					});

				    
					var timelineCollection = Gizmo.Auth(new TimelineCollection());
					timelineCollection.href.root(self.theBlog);

					self.timelineView = new TimelineView
					({
						el: $('#timeline-view .results-placeholder', self.el),
						uiCtrls: $('.timeline-controls', self.el),
						collection: timelineCollection,
						_parent: self
					});
					
					self.providers = new ProvidersView
					({
						el: $('.side ', self.el),
						providers: providers,
						_parent: self,
						theBlog: self.theBlog
					});
					self.providers.render();


					self.actions = new ActionsView
					({
						el: $('.filter-posts', self.el),
						theBlog: self.theBlog
					});
					
					$('.tabbable', self.el).find('a:eq(0)').tab('show');						
					$('.live-blog-content', self.el).droppable
					({
						activeClass: 'ui-droppable-highlight',
						accept: ':not(.edit-toolbar,.timeline)',
						drop: function(evt, ui){ self.drop(evt, ui);
						}
					});
					$("#MySplitter", self.el).splitter
					({
						type: "v",
						outline: true,
						sizeLeft: 470,
						minLeft: 470,
						minRight: 600,
						resizeToWidth: true,
						//dock: "left",
						dockSpeed: 100,
						cookie: "docksplitter",
						dockKey: 'Z',   // Alt-Shift-Z in FF/IE
						accessKey: 'I'  // Alt-Shift-I in FF/IE
					});
					$(window)
						.off(self.getNamespace())
						.on(self.getEvent('resize'), function(){
							self.responsiveTabs();
						});
					self.responsiveTabs();
					$.superdesk.hideLoader();

					self.el.find('.blog-closed-disabled').
						css('display', self.model.isClosed() ? 'block' : 'none');
					$('#site-live-info').toggle(self.model.isOpen());
				});
				/** text editor initialization */
				var editorImageControl = function()
				{
					// call super
					var command = $.ui.texteditor.prototype.plugins.controls.image.apply(this, arguments);
					// do something on insert event
					$(command).on('image-inserted.text-editor', function()
					{
						var img = $(this.lib.selectionHas('img'));
						if( !img.parents('figure.blog-image:eq(0)').length )
							img.wrap('<figure class="blog-image" />');
					});
					return command;
				},
				editorTitleControls = $.extend({}, $.ui.texteditor.prototype.plugins.controls, { image : upload.texteditor }),
				content = $(this.el).find('[is-content]'),
				titleInput = content.find('section header h2'),
				descrInput = content.find('article#blog-intro');
				delete h2ctrl.justifyRight;
				delete h2ctrl.justifyLeft;
				delete h2ctrl.justifyCenter;
				delete h2ctrl.html;
				delete h2ctrl.image;
				delete h2ctrl.link;
				delete timelinectrl.justifyRight;
                delete timelinectrl.justifyLeft;
                delete timelinectrl.justifyCenter;
                delete timelinectrl.image;
				// assign editors
				BlogAction.get('modules.livedesk.blog-edit').done(function(action) {
					titleInput.texteditor({
						plugins: {controls: h2ctrl},
						floatingToolbar: 'top'
					});
					descrInput.texteditor({
						plugins: {controls: editorTitleControls},
						floatingToolbar: 'top'
					});
				});
				/** text editor stop */
				
				
				var content = $(this.el).find('[is-content]');

				// wrapup toggle
				$(content)
				.off('click'+this.getNamespace())
				.on('click'+this.getNamespace(), 'li.wrapup', function(evt)
				{
					if(evt.target.tagName.toUpperCase() === 'A')
						return;
					if($(this).hasClass('open'))
						$(this).removeClass('open').addClass('closed').nextUntil('li.wrapup').hide();
					else
						$(this).removeClass('closed').addClass('open').nextUntil('li.wrapup').show();
				})
				.on('click'+this.getNamespace(), '.filter-posts a',function(){
					var datatype = $(this).attr('data-value');
					if(datatype == 'all') {
						$('#timeline-view li').show();
					} else {
						$('#timeline-view li').show();
						$('#timeline-view li[data-post-type!="'+datatype+'"]').hide();
					}
				})
				.on('click'+this.getNamespace(), '.collapse-title-page', function()
				{
					var intro = $('article#blog-intro', content);
					!intro.is(':hidden') && intro.fadeOut('fast') && $(this).text('Expand');
					intro.is(':hidden') && intro.fadeIn('fast') && $(this).text('Collapse');
				});
				self.textToggleStatus();
			}
		});	
	
	var 
	
	editView = new EditView({el: '#area-main'}),
	currentBlogHref = '',
	
	providerSets = 
	{
	    'full': providers,
	    'partial': $.extend({}, {edit: providers.edit})
	},
	
	load = function(theBlog)
	{
	    currentBlogHref = theBlog;
	    BlogAction.clearCache();
	    BlogAction.setBlogUrl(theBlog);
		BlogAction.get('modules.livedesk.blog-publish')
		    .done(function(){ providers = providerSets['full'] })
		    .fail(function(action){ providers = providerSets['partial'] })
		    .always(function()
		    { 
		        // stop autoupdate if any
		        editView.timelineView && editView.timelineView.collection.stop();
		        editView.theBlog = theBlog;
		        editView.postInit();
		    });
	}
	
    var AuthApp;
    require([config.cjs('views/auth.js')], function(a)
    {
        AuthApp = a;
        $(AuthApp)
        .off('.livedesks')
        .on('login.livedesk', function()
        {
            load(currentBlogHref);
        });
    });
    
    
	return load;
});
