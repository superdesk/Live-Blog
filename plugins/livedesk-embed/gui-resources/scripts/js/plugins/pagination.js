define([
	'jquery',
	'dispatcher'
], function($){
	$.dispatcher.on('posts-view.class', function(evt){
		var view = this.prototype;
		view._config.collection.limit = 10;
		view._flags.loadingNextPage = false;
		view._flags.atEnd = false;
		view.nextPage = function(){
			var self = this;
			if(self._flags.loadingNextPage || self._flags.atEnd ){
				return;	
			}
			$.dispatcher.triggerHandler('posts-view.loading', self);
			self._flags.loadingNextPage = true;
			$.each(self._config.collection, function(key, value) {
				if($.isArray(value))
					self.collection[key].apply(self.collection, value);
				else
					self.collection[key](value);
			});	
			return self.collection
					.sync().done(function(data) {
						var total = self.collection._stats.total;
						if(self._views.length >= total) {
							self._flags.atEnd = true;
						}
						self._flags.loadingNextPage = false;
						$.dispatcher.triggerHandler('posts-view.loaded', self);
					});
		}
		view.hasNextPage = function(){
			var self = this;
			return self._views.length < self.collection._stats.total;
		}
	});
});
