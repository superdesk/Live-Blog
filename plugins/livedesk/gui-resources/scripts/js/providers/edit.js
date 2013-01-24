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
    config.guiJs('livedesk', 'models/urlinfo'),
    config.guiJs('livedesk', 'models/blog'),
    'jquery/utils',
    'jquery/rest',
    'jquery/superdesk',
    'jquery/tmpl',
    'jquery/avatar',
	'jqueryui/draggable',
    'jqueryui/texteditor',
    'tmpl!livedesk>providers/edit',
    'tmpl!livedesk>providers/edit/item',
    'tmpl!livedesk>providers/edit/link',
    'tmpl!livedesk>providers/edit/urlinput',
    'tmpl!livedesk>providers/edit/image',
    'tmpl!livedesk>providers/loading',
    'tmpl!livedesk>providers/generic-error'
], function( providers, $, Gizmo, PostType, Post, uploadCom, URLInfo ) {
	var 
	
	ImagePostType = Gizmo.View.extend
	({ 
	    events:
	    {
	        ".upload-image-container": { 'click': 'add' },
	        "[data-image-source] li": { 'click': 'changeSource' },
            "[data-action='upload']": { 'change': '_upload' }
	    },
	    _restorePlace: null,
	    _isActive: false,
	    _currentSource: null,
	    changeSource: function(evt)
	    {
	        this._currentSource = $(evt.currentTarget).attr('data-source');
	        switch(this._currentSource)
	        {
	            case 'url': $('.upload-url', this.el).focus();
	        }
	    },
	    add: function(evt)
	    {
	        switch(this._currentSource)
	        {
	            case 'computer': 
	                $('[data-action="upload"]').trigger('click');
	            break;
	            
	            case 'media-archive': 
	                
	            break;
	            
	            case 'url': 
	                $('.upload-url', this.el).focus();
	            break;
	        }
	    },
	    
	    save: function()
	    {
	        
	    },
	        
	    // -- upload
        browse: function(evt)
        {
            $(evt.target).siblings('[type="file"]').trigger('click');
        },
        uploadEndPoint: $.superdesk.apiUrl+'/resources/my/Archive/MetaData/Upload?thumbSize=large&X-Filter=*&Authorization='+ localStorage.getItem('superdesk.login.session'),
        _upload: function(evt)
        {
            var uploadInput = $(evt.target),
                files = uploadInput[0].files,
                self = this; 
            for( var i=0; i<files.length; i++)
            {
                xhr = uploadCom.upload( files[i], 'upload_file', this.uploadEndPoint,
                        // display some progress type visual
                        function(){ $('[data-action="browse"]', self.el).val(_('Uploading...')); }, 'json');
                xhr.onload = function(event) 
                { 
                    $('[data-action="browse"]', this.el).val(_('Browse'));
                    try // either get it from the responseXML or responseText
                    {
                        var content = JSON.parse(event.target.responseText);
                    }
                    catch(e)
                    {
                        var content = JSON.parse(event.target.response);
                    }
                    if(!content) return;
                    $(self).triggerHandler('uploaded', [content.Id]);
                    self._latestUpload = content;
                    
                    $('.uploaded-image', self.el).html('<img src="'+content.Thumbnail.href+'" />');
                    $('.upload-url', self.el).val(content.Content.href)
                };
            }
            $('[data-action="upload"]', this.el).val('');
        },
        _latestUpload: null,
        // -- upload
        
	    show: function()
	    {
	        this._restorePlace = $(this.el).html();
	        var self = this;
	        $.tmpl('livedesk>providers/edit/image', {}, function(e, o)
	        {
	            $(self.el).html(o);
	            if(self._currentSource == null)
	                self._currentSource = $('[data-image-source] li').eq(0).attr('data-source');
	        });
	        this._isActive = true;
	    },
	    isActive: function()
	    {
	        return this._isActive;
	    },
	    restore: function()
	    {
	        $(this.el).html(this._restorePlace);
	        this._isActive = false;
	    }
	    
	}),
	imagePostType = new ImagePostType,
	
	OwnCollection = Gizmo.Collection.extend({
		insertFrom: function(model) {
			this.desynced = false;
			if( !(model instanceof Gizmo.Model) ) model = Gizmo.Auth(new this.model(model));
			this._list.push(model);
			model.hash();
			var x = model.sync(model.url.root(this.options.theBlog).xfilter(this._xfilter));
			x.done(function(data) {
				model._parseHash(data);
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
				.on('unpublish', function(){			
					self.rerender();
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
		lastType: null,
		events: {
			'[ci="savepost"]': { 'click': 'savepost'},
			'[ci="save"]': { 'click': 'save'},
			'[name="type"]' : {'change': 'changetype'}
		},
		init: function()
		{	
			var self = this,
			    PostTypes = Gizmo.Collection.extend({model: PostType});
			
			self.theBlog = self.blogUrl;
			
			self.postTypes = Gizmo.Auth(new PostTypes(self.blogUrl+'/../../../../Superdesk/PostType'));
			
			self.postTypes.on('read', function(){ self.render(); }).xfilter('Key').sync();
			
			self.blog = Gizmo.Auth(new Gizmo.Register.Blog(self.blogUrl));
			self.blog.one('read update', function(){
				self.blog.get('Type')
					.on('read.edit update.edit', function(evt){
						self.blog.get('Type').off('read.edit update.edit');
						self.blog.get('Type').get('Post')
							.one('read update', function(evt){ self.addBlogTypePosts(evt);})
							.xfilter('Id,Name,Content,Meta').sync();
					})
					.sync();

			});
			self.blog.sync();
		},
		addBlogTypePosts: function(evt){
			var self = this, 
				select = this.el.find('[name="type"]');
			var postspost = self.blog.get('Type').get('Post').feed();
			for( var i = 0, count = postspost.length; i < count; i++ ){
				var post = postspost[i];
				select.append('<option value="normal" content="'+post.Id+'">'+post.Name+'</option>');
			}
		},
		populateUrlInfo: function() {
			var self = this;

			//show loading info
			$.tmpl('livedesk>providers/loading' , {}, function(e,o) {
					self.el.find('article.editable').html(o)
				});

			var url = self.el.find('.insert-link').val();
			//search for http or https and add if not found
            if ( url.search('http://') == -1 && url.search('https://') == -1) {
                url = 'http://' + url;
            }
			var urlinfo = new URLInfo;

			urlinfo.getInfoSync(url).done(function(siteData){
				var myThumb = '';
				var favicon = "http://g.etfv.co/" + url;
				//use site image if one is provided
				if (siteData.Picture) {
					var picArr = siteData.Picture.Picture;
					if ( picArr.length > 0 ) {
						myThumb = picArr[0];
					}
				}

				//use provided site icon if given one
				if ( siteData.SiteIcon ) {
					favicon = siteData.SiteIcon;
				}

				var data = {
					url: url,
					title: siteData.Title,
					description: siteData.Description,
					thumbnail: myThumb,
					favicon: favicon
				}
				$.tmpl('livedesk>providers/edit/link' , data, function(e,o) {
					self.el.find('article.editable').html(o)
					self.el.find('.linkpost-editable').texteditor({
						plugins: {controls: {}},
						floatingToolbar: 'top'
					});
				});					
			}).fail(function() {
				//show error message
				console.log('error dude');
				$.tmpl('livedesk>providers/generic-error' , {message: 'Could not retreive site info'}, function(e,o) {
					console.log(o);
					self.el.find('article.editable').html(o)
				});
			})		
		},
		selectContent: function(evt) {
			var self = this,
				el = $(evt.target),
				currentContentId = el.find('option:selected').attr('content'),
				previous = el.data('previous'),
				post,
				previousContentId ;
			/*!
			 * If there is no previous then set previous content id to the first selection
			 */
			currentContentId = currentContentId? currentContentId: 0;
			if(!previous) {
				previousContentId = el.find('option:first').attr('content');
			} else {
				previousContentId = previous;
			}
			/*!
			 * If previous selection is a blogtype post and current is a posttype
			 *   then clear the editable html
			 */
			if(previousContentId && !currentContentId) {
				this.el.find('.edit-block article.editable').html('');
			} 
			/*!
			 * If previous selection is a posttype and the current is a blogtype post
			 *   then set editable html to blogtype post content
			 */
			else if(currentContentId) {
				var postspost = self.blog.get('Type').get('Post').feed();
				for( var i = 0, count = postspost.length; i < count; i++ ){
					post = postspost[i];
					if( currentContentId == post.Id) {
						this.el.find('.edit-block article.editable').html(post.Content);
						break;
					}
				}
			}
			el.data('previous', currentContentId);
		},
		changetype: function(evt) {
			var self = this;
			var type = self.el.find('[name="type"]').val();
			
			/*if( type == 'image' ) 
            {
                imagePostType.show();
                this.lastType = type;
                return;
            }
            else if(imagePostType.isActive())
            {
                imagePostType.restore();
                this.lastType = type;
                return;
            }*/
			
			if ( type == 'link') {
				//inject template
				$.tmpl('livedesk>providers/edit/urlinput' , {}, function(e,o) {
					self.el.find('.url-input-holder').html(o);
					self.el.find('article.editable').html('').css('height', '113px');
					self.el.find('.insert-link').unbind('keypress').bind('keypress', function(event){
						var keyCode = event.keyCode;
						if ( keyCode == 13 ) {
							self.populateUrlInfo();							
						}
					});

				});
			} else {
				if ( this.lastType == 'link' ) {
					//clear article
					self.clear();
				}
			}
			if(!evt) {
				evt = $.Event("change");
				evt.target =  self.el.find('[name="type"]');
			}
			this.selectContent(evt);
			this.lastType = type;
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
			for(var i=0; i<PostTypes.length; i++){
				if(PostTypes[i].Key == 'normal') {
					var arrPT = PostTypes.splice(i,1);
					PostTypes.unshift(arrPT[0]);
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
				
				self.changetype();
				
				// this breaks the edit area when navigation between providers
				//imagePostType.setElement( $(this).find('.edit-area') )
				
			} );
		},
		clear: function()
		{
			this.el.find('[name="type"]').val('normal');
			this.el.find('.edit-block article.editable').html('').css('height', '150px');;
			this.el.find('.url-input-holder').html('');
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
