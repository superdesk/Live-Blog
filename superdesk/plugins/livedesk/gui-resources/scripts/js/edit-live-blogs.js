define
([
    'providers/enabled',
    'gizmo/superdesk',
	'jquery',
	config.guiJs('livedesk', 'models/blog'),
	config.guiJs('livedesk', 'models/post'),
	'jquery/splitter', 'jquery/rest', 'jqueryui/droppable',
    'jqueryui/texteditor','jqueryui/sortable', 'jquery/utils', 'jquery/avatar',
    'tmpl!livedesk>layouts/livedesk',
    'tmpl!livedesk>layouts/blog',
    'tmpl!livedesk>edit',
    'tmpl!livedesk>timeline-container',
	'tmpl!livedesk>timeline-item',
	'tmpl!livedesk>provider-content',
	'tmpl!livedesk>provider-link',
	'tmpl!livedesk>providers'
], function(providers, Gizmo, $) {
	function isOnly(data,key) {
		var count = 0;
		for(i in data) {
			count++;
			if(count>1) return false;
		};
		return (data !== undefined) && (data[key] !== undefined) && (count == 1);
	}
	return function(theBlog){
		var h2ctrl = $.extend({}, $.ui.texteditor.prototype.plugins.controls);
		var
		/**
		 * Views for providers
		 * This one if for rendering of the content tab
		 */
		ProviderContentView =  Gizmo.View.extend({
			render: function(){
				var self = this,
				data = $.extend({},{link: this.name} , this.model);
				$.tmpl('livedesk>provider-content', data , function(err, out){
						self.setElement( out );
						self.model.el = self.el;
				});
				return self;
			},
		}),
		/**
		 * This rendering of the link tab, also has the event when showing the tab
		 */
		ProviderLinkView =  Gizmo.View.extend({
			events: {
				"": {"show": "show"}
			},
			render: function(){
				var self = this,
				data = $.extend({},{link: this.name} , this.model);
				$.tmpl('livedesk>provider-link', data , function(err, out){
						self.setElement( out );
				});
				return self;
			},
			show: function(evt){
				// initialize the provider init method
				this.model.init(theBlog);
			}
		}),
		/**
		 * This is the main view of the provider
		 * where is added the link tab view, content and the main html of the providers
		 */
		ProvidersView = Gizmo.View.extend({
			render: function() {
				var self = this;
				$.tmpl('livedesk>providers', self.providers , function(err, out){
					self.el.append( out );
					var links = self.el.find('ul:first'), contents = self.el.find('.tab-content:first');
					for(name in self.providers) {
						var provider = self.providers[name];
						var providerLinkView = new ProviderLinkView({ model: provider, name: name });
						var providerContentView = new ProviderContentView({ model: provider, name: name });
						links.append(providerLinkView.render().el);
						contents.append(providerContentView.render().el);
					}
				});
			}
		});
		var AutoCollection = Gizmo.Collection.extend({
			timeInterval: 10000,
			idInterval: 0,
			_latestCId: 0,
			keep: false,
			init: function(){
				//console.log('init');
			},
			destroy: function(){
				this.stop();
			},
			setIdInterval: function(fn){
				this.idInterval = setInterval(fn, this.timeInterval);
				return this;
			},
			getMaximumCid: function(data){
				for(i=0, count=data.list.length; i<count; i++) {
					var CId = parseInt(data.list[i].get('CId'))
					if( !isNaN(CId) && (this._latestCId < CId) )
						this._latestCId = CId;
				}
			},
			start: function(){
				var self = this, requestOptions = {data: {'startEx.cId': this._latestCId}, headers: { 'X-Filter': 'CId'}};
				if(self._latestCId === 0) delete requestOptions.data;
				if(!this.keep && self.view && !self.view.checkElement()) {
					self.stop();
					return;
				}
				Gizmo.Collection.prototype.sync.call(self,requestOptions).done(function(data){
					self.getMaximumCid(self.parse(data));
				});
				return this;
			},
			stop: function(){
				var self = this;
				clearInterval(self.idInterval);
				return this;
			},
			sync: function(){
				var self = this;
				this.stop().start().setIdInterval(function(){self.start();});
			}
		});
		var
		TimelineCollection = AutoCollection.extend({
			href: new Gizmo.Url('/Post/Published')
		}),
		PostView = Gizmo.View.extend({
			events: {
				'': { sortstop: 'reorder' },
				'a.close': { click: 'removeModel' },
				'.editable': { focusout: 'save' },
			},
			init: function(){
				var self = this;
				self.el.data('view', self);
				self.xfilter = 'DeletedOn, Order, Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Source.Id, IsModified, ' +
								   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id';
				this.model.off('delete read set').on('delete', this.remove, this)
					.on('read', function(){
						self.render();
					})
					.on('set', function(evt, data){
						/**
						 * If the set trrigering is the edit provider then don't update the view;
						 */
						if(self.model.updater !== self) {
							self.rerender();
						}
					})
					.on('update', function(evt, data){
						/**
						 * If the updater on the model is the current view don't update the view;
						 */
						if(self.model.updater === self) {
							delete self.model.updater; return;
						}
						/**
						 * If the Change Id is received, then sync the hole model;
						 */
						if(isOnly(data, 'CId'))
							self.model.xfilter(self.xfilter).sync();
						else {
							self.rerender();
						}
						//; self.model.xfilter(xfilter).sync();
					})
					.xfilter(self.xfilter).sync();
			},
			reorder: function(evt, ui){
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
				self.model.xfilter(self.xfilter).sync();
			},
			tightkNots: function()
			{
				if(this.next !== undefined)
					this.next.prev = this.prev;
				if(this.prev !== undefined)
					this.prev.next = this.next;				
			},
			rerender: function(){
				var self = this;
				self.el.fadeTo(500, '0.1', function(){
					self.render().el.fadeTo(500, '1');
				});
			},
			render: function(){
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
				$.tmpl('livedesk>timeline-item', {Post: this.model.feed()}, function(e, o){
					self.setElement(o).el.find('.editable').texteditor({plugins: {controls: h2ctrl}, floatingToolbar: 'top'});
				});
				return this;
			},
			save: function(){
				this.model.updater = this;
				this.model.set({Content: $(this.el).find('[contenteditable="true"]').html()}).sync();
			},
			remove: function(){
				var self = this;
				self.tightkNots();
				$(this.el).fadeTo(500, '0.1', function(){
					self.el.remove();
				});
			},
			removeModel: function(){
				var self = this;
				$('#delete-post .yes')
					.off(this.getEvent('click'))
					.on(this.getEvent('click'), function(){
						self.model.removeSync();
					});

			}
		}),

		TimelineView = Gizmo.View.extend({
			events: {
				'ul.post-list': { sortstop: 'sortstop' }
			},
			sortstop: function(evnt, ui){
				$(ui.item).triggerHandler('sortstop', ui);
			},
			init: function(){
				var self = this;
				self._latest = undefined;
				self.collection.model.off('publish').on('publish', function(evt, model){
					self.addOne(model);
				});
				self.collection
					.off('read update')
					.on('read', function(){
						self.render();
					})
					.on('update', function(evt, data){
						self.addAll(data);
					})
					.sync();
				self.collection.view = self;
			},
			addOne: function(model)
			{			
				current = new PostView({model: model, _parent: this});				
				this.el.find('ul.post-list').prepend(current.el);
				current.next = this._latest;
				if( this._latest !== undefined )
					this._latest.prev = current;
				this._latest = current;
			},
			addAll: function(data)
			{
				var next = this._latest, current, model, i = data.length;
				while(i--) {
					this.addOne(data[i]);
				}
				
			},
			render: function(){
				var self = this;
				$.tmpl('livedesk>timeline-container', {}, function(e, o){
					$(self.el).html(o)
							  .find('ul.post-list')
								.sortable({ items: 'li',  axis: 'y', handle: '.drag-bar'} ); //:not([data-post-type="wrapup"])
					self.addAll(self.collection.getList());
				});
			},
			
			/*!
			 * insert new post
			 */
			insert: function(data)
			{
			    var post = Gizmo.Auth(new this.collection.model(data));
			    this.collection.insert(post);
			},
			
			publish: function(post){
				if(post instanceof this.collection.model) {
					post.publishSync();
				} else {
					var model = new this.collection.model({ Id: data});
					this.collection.insert({})
					model.publish();
				}
				//new $.restAuth(self.blogHref + '/Post/'+post+'/Publish').resetData().insert()
			}
		}),

		EditView = Gizmo.View.extend({
			timelineView: null,
			events: {
				'[is-content] section header h2': { focusout: 'save' },
				'[is-content] #blog-intro' : { focusout: 'save' },
				//'.live-blog-content': { drop: 'drop'}
			},
			init: function(){
				var self = this;
				this.model = Gizmo.Auth(new Gizmo.Register.Blog(theBlog));
				this.model
				.off('destroy read')
				.on('read', function(){
					self.render();
				}).xfilter('Creator.Name,Creator.Id').sync();
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
				    $('ul.post-list', self.timelineView.el).prepend(either.el);
				    $('.editable', either.el).texteditor({plugins: {controls: h2ctrl}, floatingToolbar: 'top'});
				}
				else if(data !== undefined) 
					self.timelineView.insert(data);
				
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
             * TODO description
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
			
			render: function(){
				var self = this,
					data = $.extend({}, this.model.feed(), {
						BlogHref: theBlog,
						ui: {
							content: 'is-content=1',
							side: 'is-side=1',
							submenu: 'is-submenu',
							submenuActive1: 'active'
						},
					});

					$.superdesk.applyLayout('livedesk>edit', data, function(){
						// refresh twitter share button
						//require(['//platform.twitter.com/widgets.js'], function(){ twttr.widgets.load(); });
						var timelineCollection = Gizmo.Auth(new TimelineCollection( Gizmo.Register.Post ));
						timelineCollection.href.root(theBlog);
						self.timelineView = new TimelineView({
							el: $('#timeline-view .results-placeholder', self.el),
							collection: timelineCollection,
							_parent: self
						});
						self.providers = new ProvidersView({
							el: $('.side ', self.el),
							providers: providers,
							_parent: self
						});
						self.providers.render();
						$('.tabbable', self.el).find('.actived a').tab('show');						
						$('.live-blog-content', self.el).droppable({
							activeClass: 'ui-droppable-highlight',
							accept: ':not(.edit-toolbar,.timeline)',
							drop: function(evt, ui){
								self.drop(evt, ui);
							}
						});
						$("#MySplitter", self.el).splitter({
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
					topSubMenu = $(this.el).find('[is-submenu]');
					$(topSubMenu)
					.off('click.livedesk', 'a[data-target="configure-blog"]')
					.on('click.livedesk', 'a[data-target="configure-blog"]', function(event)
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
					.off('click.livedesk', 'a[data-target="edit-blog"]')
					.on('click.livedesk', 'a[data-target="edit-blog"]', function(event)
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
			}
		});
		new EditView({ el: '#area-main'});
	}
});