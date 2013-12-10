define([
	'jquery',
	'plugins',
	'plugins/user-comments-popup',
	'dispatcher',
	'tmpl!themeBase/plugins/user-comment-message',
	'tmpl!themeBase/plugins/user-comment-backdrop',
	'tmpl!themeBase/plugins/user-comment'
], function($, plugins, UserCommentsPopupView){
	return plugins["user-comments"] = function(config){
		if(!config.UserComments) {
			$.dispatcher.on('blog-view.rendered-after', function(){
				var view = this;
				$('[data-gimme="blog.comment"]',view.el).hide();
			});
			return;
		}
		$.dispatcher.on('blog-view.class', function(){
			var view = this.prototype;
			//view.events['[data-gimme="blog.comment"]'] = { "click": "userComments" };
		});
		$.dispatcher.on('blog-view.rendered-after', function(){
			var view = this;
			$.tmpl('themeBase/plugins/user-comment', {}, function(e,o){
				$('[data-gimme="blog.comment-box"]',view.el).replaceWith(o);	
			});
			$.tmpl('themeBase/plugins/user-comment-message', {}, function(e,o){
				$('[data-gimme="blog.comment-box-message"]',view.el).replaceWith(o);	
			});
			$.tmpl('themeBase/plugins/user-comment-backdrop', {}, function(e,o){
				$('[data-gimme="blog.comment-box-backdrop"]',view.el).replaceWith(o);	
			});			
			// $('[data-gimme="blog.comment-box"]',view.el).tmpl('themeBase/plugins/user-comment');
			// $('[data-gimme="blog.comment-box-message"]',view.el).tmpl('themeBase/plugins/user-comment-message');
			// $('[data-gimme="blog.comment-box-backdrop"]',view.el).tmpl('themeBase/plugins/user-comment-backdrop');
			new UserCommentsPopupView({
                    el: view.el, 
                    blogview: view,
                    model: view.model
                });
		});
	}
});