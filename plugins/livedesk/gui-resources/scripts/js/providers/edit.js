/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

define('providers/edit', [
    'providers',
	'jquery',
	'gizmo/superdesk',	
	config.guiJs('livedesk', 'models/posttype'),
	config.guiJs('livedesk', 'models/post'),
    config.guiJs('media-archive', 'upload'),
    'jquery/utils',
    'jquery/rest',
    'jquery/superdesk',
    'jquery/tmpl',
    'jquery/avatar',
	'jqueryui/draggable',
    'jqueryui/texteditor',
    'tmpl!livedesk>providers/edit',
    'tmpl!livedesk>providers/edit/item',
], function( providers, $, Gizmo, PostType, Post, uploadCom ) {
	var OwnCollection = Gizmo.Collection.extend({
		insertFrom: function(model) {
			this.desynced = false;
			if( !(model instanceof Gizmo.Model) ) model = Gizmo.Auth(new this.model(model));
			this._list.push(model);
			model.hash();
			var x = model.sync(model.url.root(this.options.theBlog).xfilter(this._xfilter));
			x.done(function(data) {
				model.set(data,{ silent: true}).clearChangeset();
			});
			x.model = model;
			return x;
		}
	}),
	PostView = Gizmo.View.extend({
		events: { 
			"": { "dragstart": "adaptor"},
			'.close': { click: 'removeDialog' }
		},
		init: function(){
			var self = this;
			self.model
				.on('read', function(){			
					self.render();
				})
				.on('set', function(evt, data){
					if(self.model.updater !== self) {
						self.rerender();
					}
				})
				.on('update', function(evt, data){ 						
					/**
					 * if the updater on the model is the current view don't update the view;
					 */
					if(self.model.updater === self) {
						delete self.model.updater; return;
					}
					/**
					 * if the Change Id is received, then sync the hole model
					 */			
					self.rerender();
				})
				.on('delete', this.remove, this);
		},
		rerender: function(){
			var self = this;
			self.el.fadeTo(500, '0.1', function(){
				self.render().el.fadeTo(500, '1');
			});
		},		
		render: function(){			
			var avatar = $.avatar.get($.superdesk.login.EMail);
			var self = this;
			if(!(this.model instanceof Gizmo.Register.Post))
				this.model = Gizmo.Auth(new Gizmo.Register.Post(this.model));
			
			var post = this.model.feed();
			if ( typeof post.Meta === 'string') {
				post.Meta = JSON.parse(post.Meta);
			}
			$.tmpl('livedesk>providers/edit/item', { Post: post, Avatar: avatar} , function(err, out){
				self.setElement( out );
				if(!self.model.get('PublishedOn')) {
							self.el.draggable({
								revert: 'invalid',
								containment:'document',
								helper: 'clone',
								appendTo: 'body',
								zIndex: 2700
							});
				}
				self.resetEvents();
			});
			return this;
		},
		remove: function(){
			var self = this;
			self.el.fadeTo(500, '0.1', function(){
				self.el.remove();
			});
		},	
		removeDialog: function(){
			var self = this;
			$('#delete-own-post .yes')
				.off(this.getEvent('click'))
				.on(this.getEvent('click'), function(){
					self.model.removeSync();
				});
		},		
		adaptor: function(evt){
			$(evt.target).parents('li').data("post", this.model);
		}
	}),
	PostsView = Gizmo.View.extend({
		init: function(){
			var self = this;
			this.posts.on('read', this.render, this);
			this.posts.model.on('insert', function(evt, model){
				self.addOne(model);
			});
			this.posts.sync();
		},
		render: function(evt, data){
			if ( data === undefined)
				data = this.posts._list;			
			for(var len = data.length, i = 0; i < len; i++ ) {
				this.addOne(data[i]);
			}
		},
		addOne: function(model)
		{
			var view = new PostView({model: model, _parent: this});
			this.el.prepend(view.render().el);
		},
		save: function(model)
		{
			var self = this;
			this.posts.insertFrom(model);
		},
		savepost: function(model)
		{
			var self = this,
			drd = this.posts.insertFrom(model);
			drd.done(function(){
				drd.model.publishSync();
			});
		}
	}),
	EditView = Gizmo.View.extend({
		postView: null,
		events: {
			'[ci="savepost"]': { 'click': 'savepost'},
			'[ci="save"]': { 'click': 'save'}
		},
		init: function()
		{	
			var self = this,
			    PostTypes = Gizmo.Collection.extend({model: PostType});
			
			self.theBlog = self.blogUrl;
			
			self.postTypes = Gizmo.Auth(new PostTypes(self.blogUrl+'/../../../../Superdesk/PostType'));
			
			self.postTypes.on('read', function(){ self.render(); }).xfilter('Key').sync();
			
		},
		render: function(){
			var self = this,
			PostTypes = this.postTypes.feed();
			for(var i=0; i<PostTypes.length; i++){
				if(PostTypes[i].Key == 'advertisement') {
					PostTypes.splice(i,1);
					break;
				}
			}
			this.el.tmpl('livedesk>providers/edit', { PostTypes: PostTypes }, function(){
				// editor 
				fixedToolbar = 
				{
					_create: function(elements)
					{
						var self = this;
						$(elements).on('toolbar-created', function()
						{
							self.plugins.toolbar.element.hide()
								.appendTo($('.edit-block .toolbar-placeholder')); 
						}); 
						$(elements).on('focusin.texteditor keydown.texteditor click.texteditor', function(event)
						{
							self.plugins.toolbar.element.fadeIn('fast');
						});
						$(elements).on('blur.texteditor focusout.texteditor', function()
						{ 
							self.plugins.toolbar.element.fadeOut('fast'); 
						});
					}
				};
				var editControls = $.extend({}, $.ui.texteditor.prototype.plugins.controls, { image : uploadCom.texteditor });
				self.el.find('.edit-block article.editable').texteditor
				({ 
				    imageDefaultWidth: null,
				    plugins: 
    				{
    				    controls: editControls,
    					floatingToolbar: null, 
    					draggableToolbar: null, 
    					fixedToolbar: fixedToolbar
    				}
				});
				var posts = Gizmo.Auth(new OwnCollection(
						self.theBlog+ '/Post/Owned?asc=createdOn', 
						Gizmo.Register.Post,
						{ theBlog: self.theBlog}
					));
				posts._xfilter = 'Id,AuthorName,Content,Type.Key,PublishedOn,CreatedOn,Author.Source.Name, Meta';
				//posts.asc('createdOn');
				posts.xfilter(posts._xfilter);
				self.postsView = new PostsView({ el: $(this).find('#own-posts-results'), posts: posts, _parent: self});
			} );
		},
		clear: function()
		{
			this.el.find('[name="type"]').val('normal');
			this.el.find('.edit-block article.editable').html('');
		},
		savepost: function(evt){
            var originalContent = $.styledNodeHtml(this.el.find('.edit-block article.editable'));
			evt.preventDefault();
			var data = {
				Content: originalContent.replace(/<br\s*\/?>\s*$/, ''),
				Type: this.el.find('[name="type"]').val()
			};
			this.clear();
			this.postsView.savepost(data);
		},
		save: function(evt){
            var originalContent = $.styledNodeHtml(this.el.find('.edit-block article.editable'));
			evt.preventDefault();
			var data = {
				Content:  originalContent.replace(/<br\s*\/?>\s*$/, ''),
				Type: this.el.find('[name="type"]').val()
			};
			this.clear();
			this.postsView.save(data);			
		}
	});	
	var editView = false;
    $.extend( providers.edit, { init: function(blogUrl)
    {
        editView = new EditView({ el: this.el, blogUrl: blogUrl }); // !editView? new EditView({ el: this.el, blogUrl: blogUrl }): editView;
    }});
	return providers;	
});