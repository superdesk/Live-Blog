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
		$.dispatcher.on('class.blog-view', function(evt){
			var view = this.prototype;			
		});
		$.dispatcher.on('rendered-before.blog-view', function(evt){
			var self = this;
			new IScroll('#wrapper', {
				bounceEasing: 'elastic',
				bounceTime: 1200,
				mouseWheel: true,
				click: true
			});
		});
	}
});