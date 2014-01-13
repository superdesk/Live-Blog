define([
	'jquery',
	'plugins',
	'dispatcher'
], function($, plugins){
	return plugins['citizen'] = function(config) {
		"use strict";

		$.dispatcher.on('class.posts-view', function(){
			var view = this.prototype;
			view._config.collection.xfilter += ', PostVerification.Status.Key';
		});

		$.dispatcher.on('rendered-after.post-view', function(evt){
			var view = this,
				postVerification = view.model.get('PostVerification'),
				statusKey = postVerification && postVerification.Status && postVerification.Status.Key;
			view.el.addClass('post-' + statusKey);
		});
	}
});