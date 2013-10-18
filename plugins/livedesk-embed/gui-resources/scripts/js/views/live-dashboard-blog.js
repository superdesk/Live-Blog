define([
	'jquery',
	'gizmo/view-events',
	'views/live-dashboard-posts',
	'dispatcher',
  'jquery/tmpl',
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
            // TODO: Show that the blog is closed
					}
				},
				render: function(){
					var self = this;
					self.el.tmpl('themeBase/container', self.model.feed(), function(){
						$.dispatcher.triggerHandler('blog-view.rendered-before', self);
						self.postsView = new PostsView({ 
							el: $('.liveblog-post-sliders',self.el),
							collection: self.model.get('PostPublished'),
							_parent: self
						});
						self.ensureStatus();
						$.dispatcher.triggerHandler('blog-view.rendered-after', self);
					});
				},
			});
		return BlogView;
	}
});
