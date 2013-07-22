define([
	'jquery',
	'dispatcher'
], function($){
	$.dispatcher.on('class-posts-view', function(evt, PostView){
		var view = this.prototype;
		view._config.limit = 2;
		view._flags.loadingNextPage = false;
		view._flags.atEnd = false;
		view.nextPage = function(){
			var self = this;
			if(self._flags.loadingNextPage || self._flags.atEnd ){
				return;	
			}
			$.dispatcher.triggerHandler('posts-view-loading', self);
			self._flags.loadingNextPage = true;
			return self.collection
					.xfilter(self._config.xfilter)
					.limit(self._config.limit)
					.offset(self.collection._stats.offset)
					.sync().done(function(data) {
						var total = self.collection._stats.total;
						if(self._views.length >= total) {
							self._flags.atEnd = true;
						}
						self._flags.loadingNextPage = false;
						$.dispatcher.triggerHandler('posts-view-loaded', self);
					});
		}
		view.hasNextPage = function(){
			var self = this;
			return !self._flags.atEnd;
		}
	});
});