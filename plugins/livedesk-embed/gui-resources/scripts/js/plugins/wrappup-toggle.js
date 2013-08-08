define([
	'jquery',
	'plugins',
	'dispatcher'
], function($, plugins){
	plugins['wrapup-toggle'] = function(config) {
		var effects = { 
			hide: 'slideUp',
			show: 'slideDown'
		};
		$.dispatcher.on('posts-view.class',function(evt){
			var view = this.prototype;
			view.events['[data-gimme="post.wrapup"]'] = {
				'click': 'wrapupToggle'
			};
			view.wrapupToggle = function(evt){
				var item = $(evt.target).closest('[data-gimme="post.wrapup"]');
					wrapupOpen = item.attr('data-wrapup-open');
				if (item.hasClass(wrapupOpen)) {
						item.removeClass(wrapupOpen);
						item.nextUntil('[data-gimme="post.wrapup"],[data-gimme="posts.nextPage"]')[effects.hide]();
					} else {
						item.addClass(wrapupOpen);
						item.nextUntil('[data-gimme="post.wrapup"],[data-gimme="posts.nextPage"]')[effects.show]();
					}
			}		
		});
	}
});