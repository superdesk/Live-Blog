define([
	'jquery',
	'plugins', 
	'plugins/button-pagination',
	'dispatcher'
], function($, plugins, buttonPaginationPlugin){
	delete plugins['button-pagination'];
	return plugins['scroll-pagination'] = function(config) {
		
		buttonPaginationPlugin(config);
		$.dispatcher.on('blog-view.class', function(evt){
			var view = this.prototype;
			view.events['[data-gimme="posts.to-top"]'] = { 'click': "toTop" }
			view.toTop = function(evt) {
				var self = this;
				$('[data-gimme="posts.list"]', self.el).scrollTop(0);
			}
		});
		$.dispatcher.on('blog-view.rendered-before', function(evt){
			var view = this;

			$('[data-gimme="posts.list"]',view.el)
				.css('overflow-y','auto')
				.css('overflow-x','hidden')
				.css('height', '500px')
		});
		$.dispatcher.on('posts-view.rendered',function(){
			var view = this;
			view.on('addingsauto addings remove', view.scrollRefresh, view)
			view.scrollRefresh();
		});
		$.dispatcher.on('posts-view.class', function(evt){
			var view = this.prototype;

			view.events[''] = { "scroll": "scrollFn"}
			view._scroll = {}
			view.scrollRefresh = function(evt){
				var self = this,
					el = $(self.el).children(':not([data-gimme="posts.beforePage"])').first();
				self._scroll = {
					el: el,
					start: el.offset().top
				}
			}
			view.scrollFn =  function(evt){
				var self = this,
					el = $(evt.target);
				if ( !self._flags.atEnd && (el.outerHeight() + 150 >= (el.get(0).scrollHeight - el.scrollTop()))) {
					self.buttonNextPage(evt);
				}

				if (self._scroll.el.offset().top < self._scroll.start) {
					//console.log('autoRender: false');
					self._flags.autoRender = false;
					//$("#liveblog-status", self.el).addClass("shadow")
				} else {
					//console.log('autoRender: true');
					self._flags.autoRender = true;
					self.addAllPending();
					//$("#liveblog-status", self.el).removeClass("shadow");
				}
			}
		});
	}
});