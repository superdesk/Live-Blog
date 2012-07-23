define([
    'providers/enabled',
    'gizmo/superdesk',
	'jquery', 
	'livedesk/models/blog',
	'livedesk/models/post',
	'jquery/splitter', 'jquery/rest', 'jqueryui/droppable',
    'jqueryui/texteditor','jqueryui/sortable', 'jquery/utils', 'jquery/avatar',
    'tmpl!livedesk>layouts/livedesk',
    'tmpl!livedesk>layouts/blog',
    'tmpl!livedesk>edit',
    'tmpl!livedesk>timeline-container',
	'tmpl!livedesk>timeline-item'],
function(providers, Gizmo, $) {
	return function(theBlog){
		var h2ctrl = $.extend({}, $.ui.texteditor.prototype.plugins.controls);
		/*var ProviderView =  Gizmo.View.extend({
			events: {
				"": {"show": "show"}
			},
			init: function(){
				this.model.el = this.model.link = this.name;
			},
			render: function(){
				var self = this;
				$.tmpl('livedesk>provider-link', this.model , function(err, out){
						self.el.link = $(out);
				});
				$.tmpl('livedesk>provider-content', this.model , function(err, out){
						self.el.link = $(out);
				});
			},
			show: function(evt){
				this.model.init(theBlog);
			}
		});
		var ProvidersView = Gizmo.View.extend({
			init: function(){
				this.render();
			}
			render: function() {							
				for(name in providers) {
					var providerView = new ProviderView({ model: providers[name], name: name});
					
				}
			}
		});*/
		var AutoCollection = Gizmo.AuthCollection.extend({
			timeInterval: 1000,			
			timerInterval: 0,
			
			auto: function(){
				this.since = 
			},
			pause: function(){
				var self=this;
				clearInterval(self.timerInterval);
			},
			start: function(){
				var self=this;
				self.timerInterval = setInterval(self.auto, self.timeInterval)
			}
		});
		var 
		TimelineCollection = Gizmo.AuthCollection.extend({
			href: new Gizmo.Url('/Post/Published')
		}),		
		PostView = Gizmo.View.extend({
			events: {
				'': { sortstop: 'reorder' },
				'a.close': { click: 'removeModel' },
				'.editable': { focusout: 'save' },
			}, 
			init: function(){
				this.model.on('delete', this.remove, this);
			},
			reorder: function(evt, ui){
				//console.log($(ui.item).attr('data-post-id'));
				var next = $(ui.item).next('li'), prev = $(ui.item).prev('li');
				if(next.length) {
					//TODO implement reordering request http://localhost/resources/LiveDesk/Blog/1/Post/7/Post/2/Reorder?before=false
					//console.log('after: '+next.attr('data-post-id'));
				} else if(prev.length){
					//TODO implement reordering request http://localhost/resources/LiveDesk/Blog/1/Post/7/Post/2/Reorder?before=false
					//console.log('before: '+prev.attr('data-post-id'));
				}
			},
			render: function(){
				var self = this;
				$.tmpl('livedesk>timeline-item', {Post: this.model.feed()}, function(e, o){
					self.setElement(o);
					$(self.el).find('.editable').texteditor({plugins: {controls: h2ctrl}, floatingToolbar: 'top'})
				});
				return this;
			},
			save: function(){
				//console.log('saved');
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
				this.posts.sync();
			},
			render: function(){
				var self = this;
				$.tmpl('livedesk>timeline-container', {}, function(e, o){
					$(self.el).html(o);
					$(self.el).find('ul.post-list').sortable({ items: 'li',  axis: 'y', handle: '.drag-bar'} ); //:not([data-post-type="wrapup"])
					self.posts.each(function(key, model){
						self.addOne(model, true);
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
				var view = new PostView({model: model, _parent: this}, { events: false, ensure: false});				
				if(order)
					$(this.el).find('ul.post-list').append(view.render().el);
				else
					$(this.el).find('ul.post-list').prepend(view.render().el);
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
				this.model = new Gizmo.Register.Blog(theBlog);
				this.model.on('read', function(){
					self.render();
				}).xfilter('Creator.Name,Creator.Id').sync();
			},
			drop: function(event, ui){
				var data = ui.draggable.data('data');
				var post = ui.draggable.data('post');
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
						var timelineCollection = new TimelineCollection( Gizmo.Register.Post );
						timelineCollection.href.root(theBlog).xfilter('Id, CId, Content, CreatedOn, Type, AuthorName, Author.Source.Name, Author.Source.Id, IsModified, ' +
								   'AuthorPerson.EMail, AuthorPerson.FirstName, AuthorPerson.LastName, AuthorPerson.Id');
						self.timeineView = new TimelineView({ 
							el: $('#timeline-view .results-placeholder', this.el),
							posts: timelineCollection,
							_parent: this								   
						});
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