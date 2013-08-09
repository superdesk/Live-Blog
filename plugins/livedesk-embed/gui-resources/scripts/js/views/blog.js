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
				self.render();
				self.auto();
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
				if(this.model.get('ClosedOn')) {
					var closedOn = new Date(this.model.get('ClosedOn'));
					this.pause();
					this.model.get('PostPublished').stop();					
					$('[data-gimme="blog.status"]',this.el).html(_('The liveblog coverage was stopped ')+closedOn.format(_('closed-date')));
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
			render: function(){
				var self = this,
					postsView;
				self.el.tmpl('themeBase/container', self.model.feed(), function(){
					$.dispatcher.triggerHandler('blog-view.after-render', self);
					self.ensureStatus();
					self.updateStatus();
					self.update();				
					postsView = new PostsView({ 
						el: $('[data-gimme="posts.list"]',self.el),
						collection: self.model.get('PostPublished'),
						_parent: self
					});
				});
			},
			update: function(){
				var self = this;
				$('[data-gimme="blog.title"]', self.el).html(self.model.get('Title'));
				$('[data-gimme="blog.description"]', self.el).html(self.model.get('Description'));
			}
		});
		$.dispatcher.triggerHandler('blog-view.class',BlogView);
		return BlogView;
	}
});