define([
	'jquery',
	'plugins', 
	'plugins/button-pagination',
	'iscroll',
	'dispatcher'
], function($, plugins, buttonPaginationPlugin, IScroll){
	delete plugins['button-pagination'];
	return plugins['scroll-pagination'] = function(config) {
		buttonPaginationPlugin(config);
		$.dispatcher.on('blog-view.class', function(evt){
			var view = this.prototype;			
		});
		$.dispatcher.on('blog-view.rendered-before', function(evt){
			var self = this;
			console.log($('[data-gimme="posts.list"]', self.el));
			new IScroll('#wrapper', {
				bounceEasing: 'elastic',
				bounceTime: 1200,
				mouseWheel: true,
				click: true
			});
		});
	}
});