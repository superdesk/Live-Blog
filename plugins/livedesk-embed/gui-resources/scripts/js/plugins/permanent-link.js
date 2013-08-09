define([
	'jquery',
	'plugins',
	'plugins/post-hash',
	'dispatcher'
], function($, plugins, postHashPlugin){
	delete plugins['post-hash'];
	return plugins['permalink'] = function(config) {
		
		postHashPlugin(config);
		var propName = 'visibility',
			propValue = { 'show': 'visible', 'hide': 'hidden' };

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
					box = $(evt.target).siblings('[data-gimme="post.share-permalink"]');
					if(box.css(propName) === propValue.show) {
						box.css(propName, propValue.hide );
					} else {
						$(evt.target).siblings('[data-gimme^="post.share"]').css(propName, propValue.hide);
						box.css(propName, propValue.show );
						box.trigger(self.getEvent('focus'));
					}		
				}
		});
	}
});