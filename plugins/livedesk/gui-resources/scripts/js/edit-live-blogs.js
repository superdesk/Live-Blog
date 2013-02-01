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
    'gizmo/superdesk/action',
	'utils/extend',
    config.guiJs('livedesk', 'models/blog'),
	config.guiJs('livedesk', 'models/posttype'),
    config.guiJs('livedesk', 'models/post'),
    'jquery/splitter', 'jquery/rest', 'jquery/param', 'jqueryui/droppable',
    'jqueryui/texteditor','jqueryui/sortable', 'jquery/utils', config.guiJs('superdesk/user', 'jquery/avatar'),
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
function(providers, Gizmo, $, Action) 
{
    // TODO rethink cause this is very ugly
    var AuthApp;
    // force homepage
    require([config.cjs('views/auth.js')], function(a)
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
			_timeInterval: 10000,
			_idInterval: 0,
			_stats: {},
			/*!
			 * for auto refresh
			 */
			keep: false,
			init: function(){ 
				var self = this;
				self._stats = { limit: 15, offset: 0, lastCId: 0, fistOrder: Infinity, total: 0 };
				self.model.on('unpublish publish reorder', function(evt, post){
					if((self._stats.lastCId + 1) === parseInt(post.get('CId')))
						self._stats.lastCId++;
				});
				self.on('readauto', function(evt, data, attr){
					// set offset to limit
					self._stats.offset = self._stats.limit;
					// set total from the attributes 
					self._stats.total = parseInt(attr.total);
					attr.lastCId = parseInt(attr.lastCId);
					if(attr.lastCId > self._stats.lastCId)
						self._stats.lastCId = attr.lastCId;
				}).on('readauto updateauto update removeingsauto',function(evt, data)
				{
					self.getLastCid(data);
					self.getFirstOrder(data);
				}).on('addingsauto', function(evt, data){
					/*!
					 * If addings ( from getting the auto updates ) 
					 *   receive we need to increase the total count of the posts and the offset
					 *   with the numbers of posts added
					 */
					self._stats.total += data.length;
					self._stats.offset += data.length;

				}).on('removeingsauto', function(evt, data){
					/*!
					 * If removeings from the collection ( from getting the autou pdates ) 
					 *   receive we need to decrease the total and the offset for the next page
					 *   with the numbers of posts added
					 */					
					self._stats.total -= data.length;
					self._stats.offset -= data.length;

				}).on('addings', function(evt, data){
					/*!
					 * If addings ( from getting the next page ) 
					 *   receive we need to increase the offset for the next page
					 *   with the numbers of posts added
					 */
					self._stats.offset += data.length;
				});
			},			
			destroy: function(){ this.stop(); },
			auto: function(fn)
			{
				var self = this;
				ret = this.stop().start();
				this._idInterval = setInterval(function(){self.start();}, this._timeInterval);
				return ret;
			},
			start: function()
			{
				var self = this, requestOptions = {data: {'cId.since': this._stats.lastCId, 'order.start': this._stats.fistOrder }, headers: { 'X-Filter': 'CId, Order, IsPublished'}};
				if(self._stats.lastCId === 0) delete requestOptions.data;
				if(!this.keep && self.view && !self.view.checkElement()) 
				{
					self.stop();
					return;
				}				
				this.triggerHandler('beforeUpdate');
				return this.autosync(requestOptions);
			},
			stop: function()
			{
				var self = this;
				clearInterval(self._idInterval);
				return this;
			},
			/*!
			 * Get the minim Order value from the post list received.
			 */
			getFirstOrder: function(data)
			{
				for(var i=0, Order, count=data.length; i<count; i++) {
					Order = parseFloat(data[i].get('Order'))
					if( !isNaN(Order) && (this._stats.fistOrder > Order) )
						this._stats.fistOrder = Order;
				}
			},
			/*!
			 * Get the maximum CId value from the post list received.
			 */			
			getLastCid: function(data)
			{
				for(var i=0, CId, count=data.length; i<count; i++) {
					var CId = parseInt(data[i].get('CId'))
					if( !isNaN(CId) && (this._stats.lastCId < CId) )
						this._stats.lastCId = CId;
				}
			},
	        autosync: function()
	        {
            var self = this;
            return (this.href &&
                this.syncAdapter.request.call(this.syncAdapter, this.href).read(arguments[0]).done(function(data)
                {					
                    var attr = self.parseAttributes(data), list = self._parse(data), changeset = [], removeings = [], updates = [], addings = [], count = self._list.length;
                     // important or it will infiloop
                    for( var i=0; i < list.length; i++ )
                    {
                        var model = false;
                        for( var j=0; j<count; j++ ) {
							if( list[i].hash() == self._list[j].hash() )
                            {
								model = list[i];
                                break;
                            }
						}
                        if( !model ) {
							if(self.isCollectionDeleted(list[i])) {
                                if( self.hasEvent('removeingsauto') ) {
                                    removeings.push(list[i]);
                                }

                            } else if( !list[i].isDeleted() ) {
								self._list.push(list[i]);
								changeset.push(list[i]);
                                if( self.hasEvent('addingsauto') ) {
                                    addings.push(list[i]);
                                }
							} else {
                                if( self.hasEvent('updatesauto') ) {
								    updates.push(list[i]);
                                }					
							}
                        }
                        else {
                            if( self.hasEvent('updatesauto') ) {
                                updates.push(model);
                            }
                            if(self.isCollectionDeleted(model)) {
                                self._list.splice(i,1);
                                if( self.hasEvent('removeingsauto') ) {
                                    removeings.push(model);
                                }

                            }
                            if( model.isDeleted()) {
                                model._remove();                               
                            } else if( model.isChanged() ){
								changeset.push(model);
							}
                            else {
                                model.on('delete', function(){ self.remove(this.hash()); })
                                        .on('garbage', function(){ this.desynced = true; });
                            }
                        }
                    }
                    self.desynced = false;
					/**
					 * If the initial data is empty then trigger READ event
					 * else UPDATE with the changeset if there are some
					 */
					if( ( count === 0) ){
						//console.log('read');

						self.triggerHandler('readauto',[self._list,attr]);
                    } else {                    
                        /**
                         * Trigger handler with changeset extraparameter as a vector of vectors,
                         * caz jquery will send extraparameters as arguments when calling handler
                         */
                        if( updates.length && self.hasEvent('updatesauto') ) {
                            self.triggerHandler('updatesauto', [updates,attr]);
                        }
                        if( addings.length && self.hasEvent('addingsauto') ) {
                            self.triggerHandler('addingsauto', [addings,attr]);
                        }
                        if( removeings.length && self.hasEvent('removeingsauto') ) {
                            self.triggerHandler('removeingsauto', [removeings,attr]);
                        }
						self.triggerHandler('updateauto', [changeset,attr]);
					}
                }));
	        }
		
		}),
		
		/*!
		 * 
		 */
		TimelineCollection = AutoCollection.extend
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
	        	return model.get('IsPublished') === 'True'? false : true;
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
				'.editable': { focusout: 'save',  focusin: 'edit'}
			},
			
			init: function()
			{
				var self = this;
				self.el.data('view', self);
				self.xfilter = 'DeletedOn, Order, Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Source.Id, IsModified, ' +
								   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id, IsPublished';
				
				this.model
				    .on('delete', this.remove, this)
				    .on('unpublish', this.remove, this)
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
					.xfilter(self.xfilter).sync({data: {thumbSize: 'medium'}});
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
			
			render: function()
			{
				var self = this, order = parseFloat(this.model.get('Order'));
				if(isNaN(order)) {
					order = 0.0;
				}
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
				var post = this.model.feed();
				post['Avatar'] = post['AuthorImage'] ? '<img src="'+post['AuthorImage'].href+'" />' :
				        '<img src="'+$.avatar.get('AuthorPerson.EMail')+'" />';
				!rendered &&
				$.tmpl('livedesk>timeline-item', {Post: post}, function(e, o)
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
				self.xfilter = 'CId, Order';
				self.collection
					.on('read readauto', function()
					{
						self.render();
						self.toggleMoreVisibility();
					})
					.on('update updateauto', function(evt, data)
					{
						self.addAll(data);
						self.toggleMoreVisibility();
					})
					.on('removeingsauto', self.removeAllAutoupdate, self)
					.xfilter(self.xfilter)
					.limit(self.collection._stats.limit)
					.offset(self.collection._stats.offset)
					.desc('order')					
					.auto();
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
				var self = this;
				self.collection
					.xfilter(self.xfilter)
					.limit(self.collection._stats.limit)
					.offset(self.collection._stats.offset)
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
				//console.log(self.model.get('PostPublished').total);
				self.total--;
				self._views.splice(pos,1);
				return self;
			},
			addOne: function(model)
			{	
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
			},
			removeAllAutoupdate: function(evt, data)
			{
				var self = this;
				for( var i = 0, count = data.length; i < count; i++ ) {
					if(data[i].postview) {
						data[i].postview.remove();
					}
				}
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
					post = Gizmo.Auth(new this.collection.model(data))
				this.collection.xfilter('CId,Order').insert(post).done(function(){
				    
				    post.href = post.data.href;
				    
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
							
				self.collection = Gizmo.Auth(new PostTypes(self.theBlog+'/../../../../Data/PostType'));
				
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
				
				this.model.xfilter('Creator.*').sync()
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
				    isOffline: function(chk, ctx){ return ctx.current().LiveOn ? "" : "hide"; }
				});
                                var creator = this.model.get('Creator').feed();
                                $.extend(data, {'creatorName':creator.Name});
				$.superdesk.applyLayout('livedesk>edit', data, function()
				{
					Action.get('modules.livedesk.blog-publish').done(function(action) {
						self.el.find('#role-blog-publish').show();
					});
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
					Action.get('modules.livedesk.configure')
					.done(function(action)
					{
						require([action.get('Script').href], function(app){ new app(blogHref); });
					});
				})
				.off(this.getEvent('click'), 'a[data-target="manage-collaborators-blog"]')
				.on(this.getEvent('click'), 'a[data-target="manage-collaborators-blog"]', function(event)
				{
					event.preventDefault();
					var blogHref = $(this).attr('href')
					Action.get('modules.livedesk.manage-collaborators')
					.done(function(action)
					{
						require([action.get('Script').href], function(app){ new app(blogHref); });
					});
				})
				.off('click'+this.getNamespace(), 'a[data-target="edit-blog"]')
				.on('click'+this.getNamespace(), 'a[data-target="edit-blog"]', function(event)
				{
					event.preventDefault();
					var blogHref = $(this).attr('href');
					Action.get('modules.livedesk.edit')
					.done(function(action)
					{
						require([$.superdesk.apiUrl+action.get('ScriptPath')], function(EditApp){ EditApp(blogHref); });
					});
				});
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
	var editView = new EditView({el: '#area-main'});
	
	return function(theBlog)
	{
	    // stop autoupdate if any
	    editView.timelineView && editView.timelineView.collection.stop();
	    
	    editView.theBlog = theBlog;
	    editView.postInit();
	}
});