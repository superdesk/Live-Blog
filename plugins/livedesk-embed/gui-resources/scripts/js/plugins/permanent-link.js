define([
	'jquery', 
	'dispatcher', 
	'plugins/post-hash',
], function($){
	var propName = 'visibility',
		propValue = { 'show': 'visible', 'hide': 'hidden' };
	
	$.dispatcher.on('post-view.class', function(evt){
		var view = this.prototype;
		view.data.permalink = view.getHash;
	});
	$.dispatcher.on('posts-view.class', function(evt){
		var view = this.prototype;
		
		view.events['[data-gimme="post.share-permalink-action"]'] = { "click": "permalinkAction" }
		view.permalinkAction = function(evt){
			evt.preventDefault();
			var self = this,
				input = $('[data-gimme="post.share-permalink-input"]',self.el);
				if(input.css(propName) === propValue.show) {
					input.css(propName, propValue.hide );
				} else {
					input.css(propName, propValue.show );
					input.trigger(self.getEvent('focus'));
					// $('.result-header .share-box', self.el).fadeOut('fast');
				}		
			}
	});
});