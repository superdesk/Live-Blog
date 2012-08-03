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
			setIdInterval: function(fn){
				this.idInterval = setInterval(fn, this.timeInterval);
				return this;
			},
			getMaximumCid: function(models){
				for (var i in models) {
					var items = models[i];
					break;
				}
				for(i=0, count=items.length; i<count; i++) {
					if( this._latestCId < parseInt(items[i].CId) )
						this._latestCId = parseInt(items[i].CId);
				}
			},
			auto: function(){
				var self = this;
				this.sync({data: {'startEx.cId': this._latestCId}, headers: { 'X-Filter': 'CId'}}).done(function(models){
					self.getMaximumCid(models);
				});
				return this;
			},                                                                                                                                                                                                                                                                              
			pause: function(){
				var self=this;
				clearInterval(self.idInterval);
			},
			start: function(){
				var self = this;
				this.auto().setIdInterval(function(){self.auto();});
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
				self.xfilter = 'Order, Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Source.Id, IsModified, ' +
								   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id';
				
				Gizmo.Auth(this.model)
				    .on('delete', this.remove, this)
					.on('read', this.render, this)
					.on('update', function(evt, data){ 
						if(isOnly(data, 'CId'))
							self.model.xfilter(self.xfilter).sync();
						else
							self.render();
						//self.el.fadeTo(500, '0.1'); self.model.xfilter(xfilter).sync(); 
					})
					.xfilter(self.xfilter).sync();
			},
			reorder: function(evt, ui){
				var next = $(ui.item).next('li'), prev = $(ui.item).prev('li');
				if(next.length) {				
					this.model.order(next.attr('data-post-id'), 'true');
				} else if(prev.length){
					this.model.order(prev.attr('data-post-id'), 'false');
				}
			},
			render: function(){
				var self = this, order = parseFloat(this.model.get('Order'));
				if ( !isNaN(self.order) && (order != self.order)) {
					var actions = { prev: 'insertBefore', next: 'insertAfter' }, ways = { prev: 1, next: -1};
					for( var dir = (self.order - order > 0)? 'next': 'prev', cursor=self[dir]; 
						(cursor[dir] !== undefined) && ( cursor[dir].order*ways[dir] < order*ways[dir] ); 
						cursor = cursor[dir]
					);
					self.el[actions[dir]](cursor.el);
				}
				self.order = order;
				$.tmpl('livedesk>timeline-item', {Post: this.model.feed()}, function(e, o){
					self.setElement(o).el.fadeTo(500, '1').find('.editable').texteditor({plugins: {controls: h2ctrl}, floatingToolbar: 'top'});
				});
				return this;
			},
			save: function(){
				this.model.set({Content: $(this.el).find('[contenteditable="true"]').html()}).sync();
			},
			remove: function(){
				var self = this;
				$(this.el).fadeTo(500, '0.1', function(){
					$(self.el).remove();
				});
			},
			removeModel: function(){
				var self = this;
				$('#delete-post .yes')
					.off(this.getEvent('click'))
					.on(this.getEvent('click'), function(){
						self.model.remove().sync();
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
				this.posts.on('read', this.render, this);
				this.posts.start();
			},
			render: function(){
				var self = this;
				$.tmpl('livedesk>timeline-container', {}, function(e, o){
					if($(self.el).find('ul.post-list:first').length === 0) {
						$(self.el).html(o)
								  .find('ul.post-list')
									.sortable({ items: 'li',  axis: 'y', handle: '.drag-bar'} ); //:not([data-post-type="wrapup"])
					}
					var current, prev = undefined;
					self.posts.each(function(key, model){
						if(model.view === undefined) {
							current = self.addOne(model, true);
							model.view = current;
							current.prev = prev;
							if( prev !== undefined )
								prev.next = current;
							prev = current;
						}
					});					
				});
			},
			insert: function(data){
				// insert new data
				//new $.restAuth(self.blogHref + '/Post/Published').resetData().insert(
			},
			publish: function(id){
				//new $.restAuth(self.blogHref + '/Post/'+post+'/Publish').resetData().insert()
			},
			addOne: function(model, order){
				var view = new PostView({model: model, _parent: this});
				if(order)
					$(this.el).find('ul.post-list').append(view.el);
				else
					$(this.el).find('ul.post-list').prepend(view.el);
				return view;
			}
		}),
		
		EditView = Gizmo.View.extend({
			timeineView: null,
			events: {
				'[is-content] section header h2': { focusout: 'save' },
				'[is-content] #blog-intro' : { focusout: 'save' },
				'.live-blog-content': { drop: 'drop'}
			},
			init: function(){
				var self = this;
				this.model = Gizmo.Auth(new Gizmo.Register.Blog(theBlog));
				this.model.on('read', function(){
					self.render();
				}).xfilter('Creator.Name,Creator.Id').sync();
			},
			drop: function(event, ui){
				var self = this, 
					data = ui.draggable.data('data'),
					post = ui.draggable.data('post');
				if(data !== undefined) {
					self.timeineView.insert(data);
				} else if(post !== undefined){
					// stupid bug in jqueryui you can make draggable desstroy
					setTimeout(function(){
						$(ui.draggable).removeClass('draggable').addClass('published').draggable("destroy");
					},1);
					self.timeineView.publish(post);
				}
			},
			save: function(evt){
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
				if(this.model.view !== undefined)
					return;
				this.model.view = this;
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
						self.timeineView = new TimelineView({ 
							el: $('#timeline-view .results-placeholder', self.el),
							posts: timelineCollection,
							_parent: self								   
						});
						self.providers = new ProvidersView({
							el: $('.side ', self.el),
							providers: providers,
							_parent: self
						});
						self.providers.render();
						$('.live-blog-content', this.el).droppable({
							activeClass: 'ui-droppable-highlight',
							accept: ':not(.edit-toolbar,.timeline)'
						});
						$("#MySplitter", this.el).splitter({
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
			}
		});
		new EditView({ el: '#area-main'});
	}    
});