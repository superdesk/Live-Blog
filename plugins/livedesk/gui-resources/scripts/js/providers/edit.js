/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

define('providers/edit', [
    'providers',
	'jquery',
	'gizmo/superdesk',
    config.guiJs('livedesk', 'action'),
	config.guiJs('livedesk', 'models/posttype'),
	config.guiJs('livedesk', 'models/post'),
    config.guiJs('media-archive', 'upload'),
    config.guiJs('livedesk', 'models/urlinfo'),
    config.guiJs('livedesk', 'models/blog'),
    config.guiJs('media-archive', 'adv-upload'),
    'jquery/utils',
    'jquery/rest',
    'jquery/superdesk',
    'jquery/tmpl',
    config.guiJs('superdesk/user', 'jquery/avatar'),
	'jqueryui/draggable',
    'jqueryui/texteditor',
    'tmpl!livedesk>items/item',
    'tmpl!livedesk>items/implementors/edit',
    'tmpl!livedesk>providers/edit',
    'tmpl!livedesk>providers/edit/item',
    'tmpl!livedesk>providers/edit/link',
    'tmpl!livedesk>providers/edit/urlinput',
    'tmpl!livedesk>providers/edit/image',
    'tmpl!livedesk>providers/edit/imageposttype',
    'tmpl!livedesk>providers/edit/imagelink',
    'tmpl!livedesk>providers/loading',
    'tmpl!livedesk>providers/generic-error',
    
], function( providers, $, Gizmo, BlogAction, PostType, Post, uploadCom, URLInfo, Blog, UploadView) {
  var uploadView = new UploadView({thumbSize: 'medium'});
	var 
	OwnCollection = Gizmo.Collection.extend({
		insertFrom: function(model) {
			this.desynced = false;
			if( !(model instanceof Gizmo.Model) ) model = Gizmo.Auth(new this.model(model));
			this._list.push(model);
			model.hash();
			model.data.Creator = localStorage.getItem('superdesk.login.id');
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
					if(self.model.get('IsPublished') === 'True') {
						self.remove();
					} else {
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
					}
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
			var self = this,
				rendered = false,
				post = self.model.feed(true),
				img = new Image;
			if(!(self.model instanceof Gizmo.Register.Post))
				self.model = Gizmo.Auth(new Gizmo.Register.Post(this.model));
			post = self.model.feed(true)
			$.avatar.setImage(post, { needle: 'Creator.EMail', size: 36});
			if ( typeof post.Meta === 'string') {
				post.Meta = JSON.parse(post.Meta);
			}
			$.tmpl('livedesk>items/item', { 
				Base: 'implementors/edit',
				Post: post
			}, function(e, output) {
				self.setElement(output);
				BlogAction.get('modules.livedesk.blog-post-publish').done(function(action) {
					//if( !self.model.get('PublishedOn')) {
						self.el.draggable({
							addClasses: false,
							revert: 'invalid',
							helper: 'clone',
							appendTo: 'body',
							zIndex: 2700,
							clone: true,
							start: function(evt, ui) {
								item = $(evt.currentTarget);;
								$(ui.helper).css('width', item.width());
							}
						});
					/*} else {
						self.el.removeClass('draggable');
					}*/
				}).fail(function(){
					self.el.removeClass('draggable');
				});
			});
			return this;
		},
		remove: function(){
			var self = this;
			self._parent.removeOne(self.model);
			delete self.model.updater;
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
			this.posts.on('read update', this.render, this);
			this.posts.model.on('insert', function(evt, model){
				self.addOne(model);
			});

			/*!
			 * @TODO: find out how this "close blog" feature supposed to work.
			 */
			//if (this._parent.blog.isOpen()) {
				this.posts.sync();
			//}
		},
		render: function(evt, data){
			if ( data === undefined)
				data = this.posts._list;	
			for(var len = data.length, i = 0; i < len; i++ ) {
				this.addOne(data[i]);
			}
		},
		removeOne: function(model) {
			var self = this,
				pos = self.posts._list.indexOf(model);
			if(pos === -1)
				return self;
			self.posts._list.splice(pos,1);
			return self;
		},
		addOne: function(model)
		{
			var view = new PostView({model: model, _parent: this});
			this.el.prepend(view.render().el);
		},
		save: function(model)
		{
			var self = this;
			var drd = this.posts.insertFrom(model);
			return drd;
		},
		savepost: function(model)
		{
			var self = this,
			drd = this.posts.insertFrom(model);
			drd.done(function(){
				drd.model.publishSync();
			});
			return drd;
		}
	}),
	collections = {},
	EditView = Gizmo.View.extend({
		postView: null,

		lastType: null,
		events: {
			'[ci="savepost"]': { 'click': 'savepost'},
			'[ci="save"]': { 'click': 'save'},
			'[name="type"]' : {'change': 'changetype'},
			'.insert-link' : {'focusout':'populateUrlInfo'},
			"[data-toggle='modal-image']": { 'click': 'openUploadScreen' }
		},
		init: function()
		{	

			var self = this,
			    PostTypes = Gizmo.Collection.extend({model: PostType});
			self.meta = {};
			self.theBlog = self.blogUrl;

			self.postTypes = Gizmo.Auth(new PostTypes(self.blogUrl+'/../../../Data/PostType'));
			
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
		handleImageUpload: function(imgData) {
			var self = this;
			if (imgData.length) {
				var myData = imgData[0].data;
				self.el.find('.upload-url').val(myData.Content.href);
				$.tmpl('livedesk>providers/edit/imagelink' , {fullimg: myData.Content.href, thumbimg:myData.Thumbnail.href}, function(e,o) {
					self.el.find('.upload-image-container .uploaded-image').html(o);
					self.el.find('.edit-block article.editable').html(o);
				});
				var myMeta = myData;
				delete myMeta.MetaInfo;
				self.meta = myMeta;
			}

		},
		openUploadScreen: function() {
			var self = this;
			uploadView.activate().then(function(data) {
				self.handleImageUpload(data);
			});
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

			self.el.find('[ci="save"]').attr('disabled', 'disabled');
			self.el.find('[ci="savepost"]').attr('disabled', 'disabled');
			
			//show loading info
			$.tmpl('livedesk>providers/loading' , {}, function(e,o) {
					self.el.find('article.editable').html(o)
				});

			var url = self.el.find('.insert-link').val();
			//search for http or https and add if not found
            if ( url.search('http://') == -1 && url.search('https://') == -1) {
                url = 'http://' + url;
            }
			var urlinfo = Gizmo.Auth(new URLInfo);

			urlinfo.getInfoSync(url).done(function(siteData){

				var pictureValid = function(url, callback) {
				  $("<img/>").attr("src", url).load(function(){
				    if (this.width > 150 && this.height >150) 
				    	filteredPicArr.push(url);
				  }); 
				}
				var filteredPicArr = [];
				var myThumb = '';
				var favicon = "http://g.etfv.co/" + url;
				//use site image if one is provided
				if (siteData.Picture) {
					var picArr = siteData.Picture.Picture;
					if ( picArr.length > 0 ) {

						//select first picture
						myThumb = filteredPicArr[0] = picArr[0];

						for( var i=1; i<picArr.length; i++) {
							if (picArr[i].indexOf("logo") != -1) {
								myThumb = picArr[i];
								filteredPicArr.push(picArr[i]);
							} else {
								pictureValid(picArr[i]);
							}
							if (filteredPicArr.length > 10) break;
						}
					}
				} 

	

				//clean the hostname for output
				var hostname = $('<a>').prop('href', url).prop('hostname');

				//use provided site icon if given one
				if ( siteData.SiteIcon ) {
					favicon = siteData.SiteIcon;
				}

				var data = {
					url: url,
					hostname: hostname,
					title: siteData.Title,
					description: siteData.Description,
					thumbnail: myThumb,
					thumbnailShow : false,
					favicon: favicon,
					siteData: siteData
				}
	
				/* extend data with embedly API response

				var scriptUrl = "http://api.embed.ly/1/oembed?url="+encodeURIComponent(url)+"&maxwidth=500";
			     $.ajax({
			        url: scriptUrl,
			        async: false,
			        success: function(response) {
			        	if (response.thumbnail_url && response.thumbnail_url.length > 0) {
			        		filteredPicArr.unshift(response.thumbnail_url);
			            	data.thumbnail = response.thumbnail_url;
			        	}
			            data.title = response.title;
			            data.description = response.description;
			        } 
			     });
				*/
				
				function updateMeta() {
					self.meta = data;
				}
				updateMeta();

				$.tmpl('livedesk>providers/edit/link' , data, function(e,o) {
					self.el.find('article.editable').html(o)
					self.el.find('.linkpost-editable').texteditor({
						plugins: {controls: {}},
						floatingToolbar: 'top'
					});

					var thumbHolder = self.el.find('.link-preview-actions');

					var iterateL = thumbHolder.find('.iterate-left');
					var iterateR = thumbHolder.find('.iterate-right')

					var thumb = self.el.find('.link-thumbnail').first();

					var toggleThumb = thumbHolder.find('.show-link-thumb');
					
					if (myThumb !== '') {
						thumbHolder.show();
						toggleThumb.prop('checked', true);
					}
					else {
						thumbHolder.hide();
						toggleThumb.prop('checked', false);
						thumb.hide();
						data.thumbnailShow = true;
						updateMeta();
					}

					var selected = 0;

					iterateL.click(function(){
						if (selected > 0) {
							selected = selected - 1;
							changeThumb(filteredPicArr[selected]);
						}
					});
					iterateR.click(function(){
						if (selected < (filteredPicArr.length-1)) {
							selected = selected + 1;
							changeThumb(filteredPicArr[selected]);
						}
					});

					
					function disableIteration() {
						if (selected == 0) 
							iterateL.addClass('disable');
						else 
							iterateL.removeClass('disable');

						if (selected == (filteredPicArr.length -1)) 
							iterateR.addClass('disable');
						else
							iterateR.removeClass('disable');
					}

					var refreshCntr = 6;
					var refreshThumbs = setInterval(function(){
						disableIteration();
						refreshCntr--;
						if (refreshCntr == 0) clearInterval(refreshThumbs);
					},500);

					toggleThumb.change(function(){
						if ($(this).is(':checked')) {
							data.thumbnailShow = true;
							thumb.show();
							changeThumb(filteredPicArr[selected]);
						} else {
							thumb.hide();
							data.thumbnailShow = false;
							updateMeta();
						}
					});

					function changeThumb(imageSource) {
						data.thumbnail = imageSource;
						thumb.find('img').attr('src',imageSource);
						disableIteration();
						updateMeta();
					}

				});	
								
			}).fail(function() {
				//show error message
				$.tmpl('livedesk>providers/generic-error' , {message: 'Could not retreive site info'}, function(e,o) {
					self.el.find('article.editable').html(o)
				});
			}).complete( function() {
				self.enableSaveButtons();
			});
		},
		enableSaveButtons: function() {
			var self = this;
			self.el.find('[ci="save"]').removeAttr('disabled');
			self.el.find('[ci="savepost"]').removeAttr('disabled');
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
			self.meta = {};
			self.enableSaveButtons();
			var type = self.el.find('[name="type"]').val();
			
            switch ( type ) {
            	case 'link':
            		self.clear();
            		//inject template
					$.tmpl('livedesk>providers/edit/urlinput' , {}, function(e,o) {
						self.el.find('.url-input-holder').html(o);
						self.el.find('article.editable').html('').addClass('link-adapted');
						self.el.find('.insert-link').unbind('keypress').bind('keypress', function(event){
							var keyCode = event.keyCode;
							if ( keyCode == 13 ) {
								self.el.find('[ci="save"]').focus();

							}
						});

					});
					break;
				case 'image':
					//inject template
					$.tmpl('livedesk>providers/edit/imageposttype' , {}, function(e,o) {
						self.el.find('.edit-area').css('display', 'none');
						self.el.find('.image-edit-area').html(o).css('display', 'inline');
					});
					break;
				default: 
					if ( this.lastType == 'link' || this.lastType == 'image') {
						//clear article
						self.clear();
					}
					break;
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
				BlogAction.get('modules.livedesk.blog-post-publish')
					.done(function(action){
						self.el.find('[ci="savepost"]').show();	
					});
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
						self.theBlog+ '/User/'+localStorage.getItem('superdesk.login.id')+'/Post/Owned?asc=createdOn&isPublished=false', 
						Gizmo.Register.Post,
						{ theBlog: self.theBlog}
					));
				posts._xfilter = 'Id,AuthorName,Content,Type.Key,PublishedOn,CreatedOn,Author.Source.Name, Meta,Creator.FullName, Creator.EMail, AuthorImage';
				//posts.asc('createdOn');
				posts.xfilter(posts._xfilter);
				collections.posts =  posts;
				self.postsView = new PostsView({ el: $(this).find('#own-posts-results'), posts: posts, _parent: self});
				
				if (self.blog.isOpen()) {
					self.changetype();
				}
			} );
		},
		clear: function()
		{
			this.el.find('.image-edit-area').html('').css('display', 'none');
			this.el.find('.edit-area').css('display', 'inline');
			this.el.find('.edit-block article.editable').html('').removeClass('link-adapted');
			this.el.find('.url-input-holder').html('');
			this.el.find('.link-preview-actions').css('display','none');
		},
		showMessage: function(type, message, timeout) {
			var self = this;
			var template = 'livedesk>providers/generic-error';
			switch (type) {
				case 'error':
					template = 'livedesk>providers/generic-error';
					break;
			}
			$.tmpl(template , {
				message: message
			}, function(e,o) {
				self.el.find('.edit-post-message').html(o);
				setTimeout(function(){
					self.el.find('.edit-post-message').html('');
				},timeout)
			});
		},
		preSave: function() {
			var self = this;
			if ( this.el.find('[name="type"]').val() == 'image' ) {
				var height = $('.input-mini-upload[data-type="image-height"]').val();
				var width = $('.input-mini-upload[data-type="image-width"]').val();
				var caption = $('.upload-caption').val();
				self.meta = $.extend({}, self.meta, {
					'height': height,
					'width': width,
					'caption': caption
				});
			}
		},
		savepost: function(evt){
			var self = this;
			self.preSave();
            var originalContent = $.styledNodeHtml(this.el.find('.edit-block article.editable'));
			evt.preventDefault();
			var data = {
				Meta: JSON.stringify(self.meta),
				Content: originalContent.replace(/<br\s*\/?>\s*$/, ''),
				Type: this.el.find('[name="type"]').val()
			};
			
			this.postsView.savepost(data).fail(function(data){
				var status = data.status;
				var responseObj = jQuery.parseJSON( data.responseText );
				var responseText = responseObj.details.model.Post.Content + _(' for text with HTML and formatting');
				switch ( status ) {
					case 400:
						self.showMessage('error', responseText, 5000);
						break;
				}
			}).done(function(){
				self.meta = {};
				self.clear();
                self.changetype();
			});
		},
		save: function(evt){
			var self = this;
			self.preSave();
            var originalContent = $.styledNodeHtml(this.el.find('.edit-block article.editable'));
			evt.preventDefault();
			var data = {
				Meta: JSON.stringify(self.meta),
				Content:  originalContent.replace(/<br\s*\/?>\s*$/, ''),
				Type: this.el.find('[name="type"]').val()
			};
			
			this.postsView.save(data).fail(function(data){
				var status = data.status;
				switch ( status ) {
					case 400:
						self.showMessage('error', _('Maximum post size is 3000 characters'), 5000);
						break;
				}
			}).done(function(){
				self.meta = {};
				self.clear();
                self.changetype();
			});			
		}
	});	
	var editView = false;
    $.extend( providers.edit, { init: function(blogUrl)
    {
        editView = new EditView({ el: this.el, blogUrl: blogUrl }); // !editView? new EditView({ el: this.el, blogUrl: blogUrl }): editView;
    },
		collections: collections
	});
	return providers;	
});
