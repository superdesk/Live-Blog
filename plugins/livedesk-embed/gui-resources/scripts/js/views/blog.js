define([
	'jquery',
	'gizmo/view-events',
	'views/posts',
	'jquery/tmpl',
	'models/blog',
	'tmpl!themeBase/container'
], function($, Gizmo, PostsView) {
	return Gizmo.View.extend({
		init: function() {
			var self = this;
			self._timeInterval = 10000;
			self._idInterval =  0;
			self.xfilter = 'Description, Title, EmbedConfig, Language.Code';
			if( !self.model ) {
				blog.url.decorate('%s/' + liveblog.id);
				blog.xfilter(self.xfilter);
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
			//self.auto();
		},
		auto: function(params)
		{
			var self = this;
			ret = self.stop();
			self._idInterval = setInterval(function(){
				self.start(params);
			}, self._timeInterval);
			return ret;
		},
		start: function(){
			var self = this;
			self.model.xfilter(self.xfilter).sync({force: true});
			return self;
		},
		stop: function(){
			var self = this;
			clearInterval(self._idInterval);
			return self;
		},			

		ensureStatus: function(){
			// if(this.model.get('ClosedOn')) {
			// 	var closedOn = new Date(this.model.get('ClosedOn'));
			// 	this.pause();
			// 	this.model.get('PostPublished').stop();					
			// 	this.el.find('#liveblog-status-time').html(_('The liveblog coverage was stopped ')+closedOn.format(_('mm/dd/yyyy HH:MM')));
			// }
		},
		updateingStatus: function(){
			this.el.find('[data-gimme="blog.sync-status"]').html(_('updating...')+'');
		},
		updateStatus: function()
		{
			var self = this,
				now = new Date();
			// if(self.model.get('ClosedOn') === undefined) {
			// 	this.el.find('#liveblog-status').fadeOut(function(){
			// 		var t = '<time data-date="'+now.getTime()+'">'+now.format(_('HH:MM'))+"</time>";
			// 		$(this).find('#liveblog-status-time')
			// 			.html(_('updated on %s').format([t])).end().fadeIn();
			// 		$.dispatcher.triggerHandler('after-render',self);
			// 	});
			// }
		},
		render: function(){
			var self = this,
				postsView;
			self.el.tmpl('themeBase/container', self.model.feed(), function(){
				self.update();
				postsView = new PostsView({ 
					el: $('[data-gimme="posts.list"]',self.el),
					collection: self.model.get('PostPublished')
				});
			});
		},
		update: function(){
			var self = this;
			$('[data-gimme="blog.title"]', self.el).html(self.model.get('Title'));
			$('[data-gimme="blog.description"]', self.el).html(self.model.get('Description'));
		}
	});
});