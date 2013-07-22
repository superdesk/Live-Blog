define([
	'jquery', 
	'dispatcher', 
	'plugins/pagination',
	'tmpl!themeBase/item/base',
	'tmpl!themeBase/plugins/button-pagination'
], function($){
	$.dispatcher.on('blog-view.after-render', function(evt, blogView){
		var view = self,
			data = {};
		data.baseItem = (require.defined('theme/item/base'))? 'theme/item/base': 'themeBase/item/base';
		$.tmpl('themeBase/plugins/button-pagination', data, function(e,o){
			$('[data-gimme="posts.list"]',view.el).append(o);
		});
	});
	$.dispatcher.on('posts-view.class', function(){
		var view = this.prototype;
		view.events['[data-gimme="posts.nextPage"]'] = {
			'click': 'buttonNextPage'
		};
		view.checkNextPage = function(evt){
			var self = this,
				item = $('[data-gimme="posts.nextPage"]',self.el);
			if(!self.hasNextPage()) {
				item.css('display','none');
			}
		}
		view.buttonNextPage = function(evt){
			var self = this,
				item = $('[data-gimme="posts.nextPage"]',self.el);
			item.addClass('loading');	
			self.nextPage().done(function(){
				item.removeClass('loading');
				self.checkNextPage();
			});
		}
	});
});