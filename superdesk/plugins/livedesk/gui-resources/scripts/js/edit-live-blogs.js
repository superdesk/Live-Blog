define
([ 
    'providers/enabled', 
    'gizmo/superdesk',
    'jquery',
	'utils/extend',
    config.guiJs('livedesk', 'models/blog'),
	config.guiJs('livedesk', 'models/posttype'),
    config.guiJs('livedesk', 'models/post'),
    'jquery/splitter', 'jquery/rest', 'jquery/param', 'jqueryui/droppable',
    'jqueryui/texteditor','jqueryui/sortable', 'jquery/utils', 'jquery/avatar',
    'tmpl!livedesk>layouts/livedesk',
    'tmpl!livedesk>layouts/blog',
    'tmpl!livedesk>edit',
    'tmpl!livedesk>timeline-container',
    'tmpl!livedesk>timeline-item',
	'tmpl!livedesk>timeline-action-item',
    'tmpl!livedesk>provider-content',
    'tmpl!livedesk>provider-link',
    'tmpl!livedesk>providers'
 ], 
function(providers, Gizmo, $) 
{
    // TODO rethink cause this is very ugly
    var AuthApp;
    // force homepage
    require([config.lib_js_urn + 'views/auth'], function(a)
    {
        AuthApp = a;
        $(AuthApp).on('logout', function()
        {
            window.location.reload();
        });
    });
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
		 * Extended collection which is autoupdateing itself
		 */
		AutoCollection = Gizmo.Collection.extend
		({
			timeInterval: 10000,
			idInterval: 0,
			_latestCId: 0,
			/*!
			 * for auto refresh
			 */
			keep: false,
			init: function(){ 
				var self = this;
				self.model.on('publish reorder', function(evt, data){
					self.getMaximumNearCid(self.parse([data]));
				});
				this.on('read update updates',function(evt, data)
				{
					if(!data)
						data = self._list;
					self.getMaximumCid(self.parse(data));
				});
			},
			destroy: function(){ this.stop(); },
			setIdInterval: function(fn)
			{
				this.idInterval = setInterval(fn, this.timeInterval);
				return this;
			},
			getMaximumNearCid: function(data)
			{
				for(i=0, count=data.list.length; i<count; i++) {
					var CId = parseInt(data.list[i].get('CId'))
					if( !isNaN(CId) && (this._latestCId < CId) && ((this._latestCId + 1) == CId))
						this._latestCId = CId;
				}
			},
			getMaximumCid: function(data)
			{
				for(i=0, count=data.list.length; i<count; i++) {
					var CId = parseInt(data.list[i].get('CId'))
					if( !isNaN(CId) && (this._latestCId < CId) )
						this._latestCId = CId;
				}
			},
			start: function()
			{
				var self = this, requestOptions = {data: {'cId.since': this._latestCId}, headers: { 'X-Filter': 'CId, Order'}};
				if(self._latestCId === 0) delete requestOptions.data;
				if(!this.keep && self.view && !self.view.checkElement()) 
				{
					self.stop();
					return;
				}				
				return this.sync(requestOptions);
				return this;
			},
			stop: function()
			{
				var self = this;
				clearInterval(self.idInterval);
				return this;
			},
			autosync: function()
			{
				var self = this,
				ret = this.stop().start();
				this.setIdInterval(function(){self.start();});
				return ret;
			}
		
		}),
		
		/*!
		 * 
		 */
		TimelineCollection = AutoCollection.extend
		({
			model: Gizmo.Register.Post,
			href: new Gizmo.Url('/Post/Published')
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
				'.editable': { focusout: 'save',  focusin: 'edit'}
			},
			
			init: function()
			{
				var self = this;
				self.el.data('view', self);
				self.xfilter = 'DeletedOn, Order, Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Source.Id, IsModified, ' +
								   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id';
				this.model
				    .on('delete', this.remove, this)
					.on('read', function()
					{
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
					    /*!
                         * conditionally handing over save functionality to provider if
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
                        
						/*!
						 * If the updater on the model is the current view don't update the view;
						 */
						if(self.model.updater === self) {
							delete self.model.updater; return;
						}
						if(data['Order'])
							self.order = parseFloat(data['Order']);
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
					.xfilter(self.xfilter).sync();
			},
			
			reorder: function(evt, ui)
			{
				var self = this, next = $(ui.item).next('li'), prev = $(ui.item).prev('li'), id, order, newPrev = undefined, newNext = undefined;
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
				if(this.next !== undefined)
					this.next.prev = this.prev;
				if(this.prev !== undefined)
					this.prev.next = this.next;				
			},
			
			rerender: function()
			{
				var self = this;
				self.el.fadeTo(500, '0.1', function(){
					self.render().el.fadeTo(500, '1');
				});
			},
			
			render: function()
			{
				var self = this, order = parseFloat(this.model.get('Order'));
				if ( !isNaN(self.order) && (order != self.order) && this.model.ordering !== self) {
					var actions = { prev: 'insertBefore', next: 'insertAfter' }, ways = { prev: 1, next: -1}, anti = { prev: 'next', next: 'prev'}
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
				
				// pre parse data
				var src = self.model.get("Author").Source.Name,
				    rendered = false;
				// pass functionallity to provider if exists
				if( providers[src] && providers[src].timeline )
				{
				    providers[src].timeline.preData && providers[src].timeline.preData.call(self);
				    if( providers[src].timeline.render ) 
				    {
				        providers[src].timeline.render.call(self, function()
				        {
				            $('.editable', this.el).texteditor({plugins: {controls: timelinectrl}, floatingToolbar: 'top'});
				            
				            $(self).triggerHandler('render');
				        });
				        rendered = true;
				    }
				}
				var posts = this.model.feed();
				posts = $.avatar.parse(posts, 'AuthorPerson.EMail');
				!rendered &&
				$.tmpl('livedesk>timeline-item', {Post: posts}, function(e, o)
				{
					self.setElement(o).el.find('.editable')
					    .texteditor({plugins: {controls: timelinectrl}, floatingToolbar: 'top'});
					
					/*!
                     * conditionally handing over some functionallity to provider if
                     * model has source name in providers 
                     */
                    if( providers[src] && providers[src].timeline ) {
						providers[src].timeline.init.call(self);
					}
                    
                    $(self).triggerHandler('render');
					
				});
				
				//this.el.siblings().removeClass('first').eq('0').nextUntil('[data-post-type=wrapup]').andSelf().addClass('first');
				
				return this;
			},
			
			/*!
			 * subject to aop
			 */
			preData: $.noop,
			edit: $.noop,
			save: function(evt)
			{
				if($(evt.target).data('linkCommandActive'))
					return;
				this.model.updater = this;
				this.model.set({Content: $(this.el).find('[contenteditable="true"]').html()}).sync();
			},		
			remove: function()
			{
				var self = this;
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

			}
		}),

		TimelineView = Gizmo.View.extend
		({
			limit: 25,
			offset: 0,
			events: 
			{
				'ul.post-list': { sortstop: 'sortstop' },
				'#more': { click: 'more' }
			},
			init: function()
			{
				var self = this;
				self._latest = undefined;
				self._views = [];
				self.collection.model.on('publish', function(evt, model){
					self.addOne(model);
				});
				self.xfilter = 'CId, Order';
				self.collection
					.on('read', function()
					{
						self.render();
					})
					.on('update', function(evt, data)
					{
						self.addAll(data);
					})
					.xfilter(self.xfilter)
					.limit(self.limit)
					.offset(self.offset)
					.autosync().done(function(data){
						if(parseInt(data.total)<= self.limit) {
							$('#more').hide();
						}
					});
				self.collection.view = self;
				
				// default autorefresh on
				localStorage.setItem('superdesk.config.timeline.autorefresh', 1);
				// toggle autorefresh
				$('[data-toggle="autorefresh"]', self.uiCtrls).off('click')
				    .on('click', function(){ self.configAutorefresh.call(self, this); })
				    .tooltip({placement: 'bottom'});
				
			},
			more: function(evnt, ui)
			{
				var self = this,
					offset = $(evnt.target).data('offset');
				offset = offset? offset: 1;
				self.collection
					.xfilter(self.xfilter)
					.limit(self.limit)
					.offset(offset*self.limit)
					.sync().done(function(data){
						self.total = parseInt(data.total);
						if((offset+1)*self.limit >= self.total)
							$(evnt.target).hide();
					});
				$(evnt.target).data('offset', offset+1);
			},
			sortstop: function(evnt, ui)
			{
				$(ui.item).triggerHandler('sortstop', ui);
			},			
			addOne: function(model)
			{	
				if(model.postview && model.postview.checkElement())
					return;
				var self = this,
					current = new PostView({model: model, _parent: self}),				    
					count = self._views.length;
				model.postview = current;
				current.order =  parseFloat(model.get('Order'));
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
					
					/*current.next = this._latest;
					if( this._latest !== undefined )
						this._latest.prev = current;
					this._latest = current;
					*/					
				}
				$(current).on('render', function(){ self.autorefreshHandle.call(self, current.el.outerHeight(true)); });
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
				$.tmpl('livedesk>timeline-container', {}, function(e, o)
				{
					$(self.el).html(o)
					    .find('ul.post-list')
					    .sortable({ items: 'li',  axis: 'y', handle: '.drag-bar'} ); //:not([data-post-type="wrapup"])
					self.addAll(self.collection.getList());
				});
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
					post = Gizmo.Auth(new this.collection.model(data))
				this.collection.xfilter('CId,Order').insert(post).done(function(){
					self.collection.model.triggerHandler('publish', post);
					self.addOne(post);		
				});
				if(view) {
					view.el.remove();
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
			    if( parseFloat(localStorage.getItem('superdesk.config.timeline.autorefresh')) ) return;
			    
			    var x = $('.live-blog-content').parents(':eq(0)').scrollTop();
			        $('.live-blog-content').parents(':eq(0)').scrollTop( x + newH );
			    
			},
			/*!
			 * configure autorefresh on timeline
			 * 0 is for no refresh
			 * 
			 */
			configAutorefresh: function(button)
            {
			    var cnfAuto = localStorage.getItem('superdesk.config.timeline.autorefresh');
	            if( !parseFloat(cnfAuto) )
	            {
	                localStorage.setItem('superdesk.config.timeline.autorefresh', 1);
	                $(button).removeClass('active');
	            }
	            else
	            {
	                this.stoppedHeight = false;
	                localStorage.setItem('superdesk.config.timeline.autorefresh', 0);
	                $(button).addClass('active');
	            }
            }
		}),
		ActionsView = Gizmo.View.extend
		({
			init: function() {
				var self = this,
					PostTypes = Gizmo.Collection.extend({model: Gizmo.Register.PostType});
							
				self.collection = Gizmo.Auth(new PostTypes(self.theBlog+'/../../../../Superdesk/PostType'));
				
				self.collection.on('read', function(){ self.render(); }).xfilter('Key').sync();				
			},
			render: function(){
				var self = this,
					PostTypes = this.collection.feed();
				this.el.tmpl('livedesk>timeline-action-item', { PostTypes: PostTypes }, function(){				
					var self = this;
				});
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
				//, '.live-blog-content': { drop: 'drop'}
				'#put-live .btn-primary': { click : 'putLive' },
				'#more': { click: 'more'}
			},
			more: function(evnt)
			{
				this.timelineView.more(evnt);
			},			
			postInit: function()
			{
				var self = this;
				this.model = Gizmo.Auth(new Gizmo.Register.Blog(self.theBlog));
				
				this.model.xfilter('Creator.Name').sync()
				    // once
				    .done(function()
				    {
				        self.model.get('Admin').on('read', function(){ self.render.call(self); }).xfilter('*').sync();
				    });
			},
			/*!
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
					self.timelineView.insert(data);
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
				var content = $(this.el).find('[is-content]'),
				titleInput = content.find('section header h2'),
				descrInput = content.find('article#blog-intro'),
				data = {
						Title: $.styledNodeHtml(titleInput),
						Description: $.styledNodeHtml(descrInput)
				};
				this.model.set(data).sync().done(function() {
					content.find('.tool-box-top .update-success').removeClass('hide')
					setTimeout(function(){ content.find('.tool-box-top .update-success').addClass('hide'); }, 5000);
				})
				.fail(function() {
					content.find('.tool-box-top .update-error').removeClass('hide')
					setTimeout(function(){ content.find('.tool-box-top .update-error').addClass('hide'); }, 5000);
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
                        msgOffline = $('#put-live-msg-offline', self.el);
                    if( stsLive.hasClass('hide') )
                    {
                        stsLive.removeClass('hide');
                        stsOffline.addClass('hide');
                        msgLive.addClass('hide');
                        msgOffline.removeClass('hide');
                        return;
                    }
                    stsLive.addClass('hide');
                    stsOffline.removeClass('hide');
                    msgLive.removeClass('hide');
                    msgOffline.addClass('hide');
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
					self.textToggleStatus();
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
				data = $.extend({}, this.model.feed(), 
				{
					BlogHref: self.theBlog,
					ui: 
					{
						content: 'is-content=1',
						side: 'is-side=1',
						submenu: 'is-submenu',
						submenuActive1: 'active'
					},
				    isLive: function(chk, ctx){ return ctx.current().LiveOn ? "hide" : ""; },
				    isOffline: function(chk, ctx){ return ctx.current().LiveOn ? "" : "hide"; },
				    isCreatorOrAdmin: (function()
				    { 
				        var userId = localStorage.getItem('superdesk.login.id');
				        if( self.model.get('Creator').get('Id') == userId) return true;
				        self.model.get('Admin').each(function()
				        { 
				            if(this.get('Id') == userId) return true;
				        });  
				        return false;
				    })()
				});
                                var creator = this.model.get('Creator').feed();
                                $.extend(data, {'creatorName':creator.Name});
				$.superdesk.applyLayout('livedesk>edit', data, function()
				{
					// refresh twitter share button
					//require(['//platform.twitter.com/widgets.js'], function(){ twttr.widgets.load(); });
				    
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
					
					$.superdesk.hideLoader();
					
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
				editorTitleControls = $.extend({}, $.ui.texteditor.prototype.plugins.controls, { image : editorImageControl }),
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
                delete timelinectrl.html;
                delete timelinectrl.image;
				// assign editors
				titleInput.texteditor({
					plugins: {controls: h2ctrl},
					floatingToolbar: 'top'
				});
				descrInput.texteditor({
					plugins: {controls: editorTitleControls},
					floatingToolbar: 'top'
				});
				/** text editor stop */
				
				
				var 
					topSubMenu = $(this.el).find('[is-submenu]'),
					content = $(this.el).find('[is-content]');
				$(topSubMenu)
				.off('click'+this.getNamespace(), 'a[data-target="configure-blog"]')
				.on('click'+this.getNamespace(), 'a[data-target="configure-blog"]', function(event)
				{
					event.preventDefault();
					var blogHref = $(this).attr('href')
					$.superdesk.getAction('modules.livedesk.configure')
					.done(function(action)
					{
						action.ScriptPath && 
							require([$.superdesk.apiUrl+action.ScriptPath], function(app){ new app(blogHref); });
					});
				})
				.off('click'+this.getNamespace(), 'a[data-target="edit-blog"]')
				.on('click'+this.getNamespace(), 'a[data-target="edit-blog"]', function(event)
				{
					event.preventDefault();
					var blogHref = $(this).attr('href');
					$.superdesk.getAction('modules.livedesk.edit')
					.done(function(action)
					{
						action.ScriptPath && 
							require([$.superdesk.apiUrl+action.ScriptPath], function(EditApp){ EditApp(blogHref); });
					});
				});
				// wrapup toggle
				$(content)
				.off('click'+this.getNamespace())
				.on('click'+this.getNamespace(), 'li.wrapup', function()
				{
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
	var editView = new EditView({el: '#area-main'});
	
	return function(theBlog)
	{
	    // stop autoupdate if any
	    editView.timelineView && editView.timelineView.collection.stop();
	    
	    editView.theBlog = theBlog;
	    editView.postInit();
	}
});