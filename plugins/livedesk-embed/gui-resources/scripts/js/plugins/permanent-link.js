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
		view.events['[data-gimme="post.share-permalink"]'] = { "click focus": "permalinkInput" }
		view.permalinkInput = function(evt){
			$(evt.target).select();
		}

		view.events['[data-gimme="post.permalink"]'] = { "click": "permalinkAction" }
		view.permalinkAction = function(evt){
			evt.preventDefault();
			var self = this,
				box = $('[data-gimme="post.share-permalink"]',self.el);
				if(box.css(propName) === propValue.show) {
					box.css(propName, propValue.hide );
				} else {
					$('[data-gimme^="post.share"]',self.el).css(propName, propValue.hide);
					box.css(propName, propValue.show );
					box.trigger(self.getEvent('focus'));
				}		
			}
	});
});