define([
	'jquery', 
	'dispatcher', 
	'plugins/pagination',
	'tmpl!themeBase/item/base',
	'tmpl!themeBase/plugins/after-button-pagination',
	'tmpl!themeBase/plugins/before-button-pagination'
], function($){
	$.dispatcher.on('blog-view.after-render', function(evt, blogView){
		var view = self,
			data = {};
		data.baseItem = (require.defined('theme/item/base'))? 'theme/item/base': 'themeBase/item/base';
		$.tmpl('themeBase/plugins/before-button-pagination', data, function(e,o){
			$(o)
				.css('display','none')
				.prependTo('[data-gimme="posts.list"]',view.el);
		});
		$.tmpl('themeBase/plugins/after-button-pagination', data, function(e,o){
			$(o)
				.appendTo('[data-gimme="posts.list"]',view.el);
		});
		$('[data-gimme="posts.list"]')
			.css('overflow-y','auto')
			.css('overflow-x','hidden')
			.css('height', '500px');
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