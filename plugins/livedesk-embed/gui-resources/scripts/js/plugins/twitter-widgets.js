requirejs.config({
    paths: { "twitterWidgets": "//platform.twitter.com/widgets" }
}); 
define([
	'jquery',
	'plugins',
	'dust',
	'jquery/waypoints',
	'dispatcher',
	'twitterWidgets'
], function($, plugins, dust, waypoints){
	return plugins["twitter-widgets"] = function(config){
		$.dispatcher.on('post-view.rendered-after-/item/source/twitter', function(){
			var self = this;
			if(!self._parent._waypoints)
				self._parent._waypoints = [];
			self._parent._waypoints.push(self.el);
			self.el.waypoint(function(dir){
				window.twttr.widgets.createTweet(
					self.templateData.Meta.id_str,
					self.el.find('.post-content-full').get(0),
					function(){
						self.el.find('.post-core-content').remove();
					},
					{ cards: 'all' }
				);
			}, {
				triggerOnce: true,
				enabled: false,
				offset: '120%',
				context: self._parent.el
			});
		});
		$.dispatcher.on('posts-view.rendered', function(){
			var self = this;
			for(var i = 0, count = self._waypoints.length; i < count; i++) {
				console.log(self._waypoints[i]);
				self._waypoints[i].waypoint('enable');
			}
			self._waypoints = [];
		});
	}
});