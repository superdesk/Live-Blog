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
    'jquery/utils',
    'jquery/rest',
    'jquery/superdesk',
    'jquery/tmpl',
    'jquery/avatar',
	'jqueryui/draggable',
    'jqueryui/texteditor',
    'tmpl!livedesk>providers/edit',
    'tmpl!livedesk>providers/edit/item',
], function( providers, $, Gizmo ) {
	var OwnCollection = Gizmo.Collection.extend({
		insertFrom: function(model) {
			this.desynced = false;
			if( !(model instanceof Gizmo.Model) ) model = Gizmo.Auth(new this.model(model));
			this._list.push(model);
			model.hash();
			var x = model.sync(model.url.root(this.options.theBlog).xfilter('Id,AuthorName,Content,Type.Key,PublishedOn,CreatedOn,Author.Source.Name'));
			return x;			
		}
	}),
	PostView = Gizmo.View.extend({
		events: { 
			"": { "dragstart": "adaptor"}
		},
		init: function(){
			this.model.on('read', function(){
				
				this.render();
			}, this);
			this.model.on('update', this.render, this);
		},
		render: function(){			
			var avatar = $.avatar.get($.superdesk.login.EMail);
			var self = this;
			if(!(this.model instanceof Gizmo.Register.Post))
				this.model = Gizmo.Auth(new Gizmo.Register.Post(this.model));
			$.tmpl('livedesk>providers/edit/item', { Post: this.model.feed(),Avatar: avatar} , function(err, out){
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
		adaptor: function(evt){
			$(evt.target).parents('li').data("post", this.model.get('Id'));
		}
	}),
	PostsView = Gizmo.View.extend({
		init: function(){
			var self = this;
			this.posts.on('read', function(){
				self.render();
			});
			this.posts.model.on('insert', function(evt, model){
				self.addOne(model);
			});
			this.posts.sync();
		},
		render: function(){
			var self = this;
			this.posts.each(function(key, model){
				self.addOne(model, true);
			});
		},
		insert: function(model)
		{
			var self = this;
			this.posts.insertFrom(model);
		},
		addOne: function(model, order)
		{
			var view = new PostView({model: model, _parent: this});
			if(order)
				this.el.append(view.render().el);
			else
				this.el.prepend(view.render().el);
		}
	}),
	EditView = Gizmo.View.extend({
		postView: null,
		events: {
			'[ci="savepost"]': { 'click': 'savepost'},
			'[ci="save"]': { 'click': 'save'}
		},
		init: function(){			
			this.postTypes = new Gizmo.AuthCollection(this.theBlog+'/../../../../Superdesk/PostType', Gizmo.Register.PostType);
			this.postTypes.xfilter('Key');;
			this.postTypes.on('read', this.render, this);
			this.postTypes.sync();
		},
		render: function(){
			var self = this;
			this.el.tmpl('livedesk>providers/edit', { PostTypes: this.postTypes.feed() }, function(){
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
				self.el.find('.edit-block article.editable').texteditor({ plugins: 
				{
					floatingToolbar: null, 
					draggableToolbar: null, 
					fixedToolbar: fixedToolbar
				}});
				var posts = Gizmo.Auth(new OwnCollection(
						self.theBlog+ '/Post/Owned?X-Filter=Id,AuthorName,Content,Type.Key,PublishedOn,CreatedOn,Author.Source.Name', 
						Gizmo.Register.Post,
						{ theBlog: self.theBlog}
					));
				//posts.xfilter('Id,AuthorName,Content,Type.Key,PublishedOn,CreatedOn,Author.Source.Name');
				self.postsView = new PostsView({ el: $(this).find('#own-posts-results'), posts: posts, _parent: self});
			} );
		},
		savepost: function(evt){
			evt.preventDefault();
			var data = {
				Content: $.styledNodeHtml(this.el.find('.edit-block article.editable')),
				Type: this.el.find('[name="type"]').val()
			};
			this.postsView.insert(data);
		},
		save: function(evt){
			evt.preventDefault();
			
		}
	});	
	$.extend( providers.edit, { 
		init: function(theBlog){ 
			new EditView({ el: this.el, theBlog: theBlog }); 
		}
	});
	return providers;	
});