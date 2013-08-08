define([
	'jquery', 
	'dispatcher', 
	'plugins/button-pagination'
], function($){
	$.dispatcher.on('blog-view.after-render', function(evt){
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
				self._flags.autoRender = false;
				//$("#liveblog-status", self.el).addClass("shadow")
			} else {
				self._flags.autoRender = true;
				self.addAllPending();
				//$("#liveblog-status", self.el).removeClass("shadow");
			}
		}
	});
});