define([
	'jquery', 
	'dispatcher', 
	'plugins/pagination',
	'tmpl!themeBase/item/base',
	'tmpl!themeBase/plugins/after-button-pagination',
	'tmpl!themeBase/plugins/before-button-pagination'
], function($){

	var propName = 'display',
		propValue = { 'show': 'block', 'hide': 'none' };

	$.dispatcher.on('posts-view.rendered', function(evt){
		var view = self,
			data = {};
		data.baseItem = (require.defined('theme/item/base'))? 'theme/item/base': 'themeBase/item/base';
		$.tmpl('themeBase/plugins/before-button-pagination', data, function(e,o){
			$(o)
				.css(propName,propValue.hide)
				.prependTo('[data-gimme="posts.list"]',view.el);
		});
		$.tmpl('themeBase/plugins/after-button-pagination', data, function(e,o){
			$(o)
				.css(propName,propValue.hide)
				.appendTo('[data-gimme="posts.list"]',view.el);
		});
	});
	$.dispatcher.on('posts-view.class', function(){
		var view = this.prototype;
		view.events['[data-gimme="posts.nextPage"]'] = {
			'click': 'buttonNextPage'
		};
		view.events['[data-gimme="posts.beforePage"]'] = {
			'click': 'buttonBeforePage'
		};
		view.checkBeforePage = function(evt){			
			var self = this,
				item = $('[data-gimme="posts.beforePage"]',self.el);
			if(!self._flags.beforePage) {
				item.css(propName,propValue.hide);
			} else {
				item.css(propName,propValue.show);
			}
		}
		view.checkNextPage = function(evt){
			var self = this,
				item = $('[data-gimme="posts.nextPage"]',self.el);
			if(!self.hasNextPage()) {
				item.css(propName,propValue.hide);
			} else {
				item.css(propName,propValue.show);
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

		view.buttonBeforePage = function(evt){
			var self = this,
				item = $('[data-gimme="posts.beforePage"]',self.el);
			item.addClass('loading');
			$(self.el).html('');			
			self.beforePage().done(function(){
				item.removeClass('loading');
				self._flags.beforePage = false;
				item.css(propName,propValue.hide);
			});

		}
	});
	$.dispatcher.on('posts-view.rendered', function(){
		this.checkNextPage();
		this.checkBeforePage();
	});
});