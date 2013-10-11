define([
	'jquery',
	'gizmo/view-events',
	'views/posts',
	'dispatcher',
	'jquery/tmpl',
	'models/blog',
	'tmpl!themeBase/container'
], function($, Gizmo, PostsViewDef) {
	return function(){
		var PostsView = PostsViewDef(),
			BlogView = Gizmo.View.extend({
				events: {},
				_config: {
					timeInterval: 10000,
					idInterval: 0,
					xfilter: 'Description, Title, EmbedConfig, Language.Code'
				},
				init: function() {
					var self = this;
					if( !self.model ) {
						blog.url.decorate('%s/' + liveblog.id);
						blog.xfilter(self._config.xfilter);
					}
					self.model.on('update', function(e, data){
						self.ensureStatus();
						self.update();
					}).on('sync',function(){
						self.updateingStatus();
					})
					.on('synced', function(){
						self.updateStatus();
					});
					self.auto();
					self.render();
				},
				auto: function(params)
				{
					var self = this;
					ret = self.stop();
					self._config.idInterval = setInterval(function(){
						self.start(params);
					}, self._config.timeInterval);
					return ret;
				},
				start: function(){
					var self = this;
					self.model.xfilter(self._config.xfilter).sync({force: true});
					return self;
				},
				stop: function(){
					var self = this;
					clearInterval(self._config.idInterval);
					return self;
				},			

				ensureStatus: function(){
					var self = this,
						closedOn;
					if(self.model.get('ClosedOn')) {
						closedOn = new Date(self.model.get('ClosedOn'));
						self.stop();
						self.model.get('PostPublished').stop();
						$('[data-gimme="blog.status"]',self.el).html(_('The liveblog coverage was stopped ')+closedOn.format(_('closed-date')));
					}
				},
				updateingStatus: function() {
					$('[data-gimme="blog.status"]',this.el).html(_('updating...')+'');
				},
				updateStatus: function() {
					var self = this,
						now = new Date();
					if(self.model.get('ClosedOn') === undefined) {
						var t = '<time data-date="'+now.getTime()+'">'+now.format(_('status-date'))+"</time>";
						$('[data-gimme="blog.status"]',self.el)
								.html(_('updated on %s').format([t]));
					}
				},
				hideNewPosts: function(){
					$('[data-gimme="posts.pending-message"]',self.el)
						.html('')
						.hide();
				},
				showNewPosts: function(n){
					var self = this;
					$('[data-gimme="posts.pending-message"]',self.el)
						.html(ngettext('one new post', '%(count)s new posts',n ).format( { count: n}))
						.show();
				},
				render: function(){
					var self = this;
					self.el.tmpl('themeBase/container', self.model.feed(), function(){
						$.dispatcher.triggerHandler('blog-view.rendered-before', self);
						self.update();
						self.postsView = new PostsView({ 
							el: $('[data-gimme="posts.list"]',self.el),
							collection: self.model.get('PostPublished'),
							_parent: self
						});
						self.ensureStatus();
						self.updateStatus();
						$.dispatcher.triggerHandler('blog-view.rendered-after', self);
					});
				},
				update: function(){
					var self = this, embedConfig = {} ;

					embCnfg = self.model.get('EmbedConfig')
					try {
						embedConfig = JSON.parse(embCnfg);
					} catch(e){
						//handle it
					}

					if ( typeof(embedConfig.MediaToggle) != 'undefined' ) {
						if ( embedConfig.MediaToggle ) {
							$('[data-gimme="blog.media-toggle"]', self.el).css('display', 'block' );
						} else {
							$('[data-gimme="blog.media-toggle"]', self.el).css('display', 'none' );
						}
					} else {
						//do nothing 
					}

					if ( embedConfig.MediaUrl ) {
						$('[data-gimme="blog.media-url"]', self.el).attr('href', embedConfig.MediaUrl );
					}
					if ( embedConfig.MediaImage ) {
						$('[data-gimme="blog.media-image"]', self.el).attr('src', embedConfig.MediaImage );
					}

					$('[data-gimme="blog.title"]', self.el).html(self.model.get('Title'));
					$('[data-gimme="blog.description"]', self.el).html(self.model.get('Description'));
				}
			});
		$.dispatcher.triggerHandler('blog-view.class',BlogView);
		return BlogView;
	}
});