requirejs.config({
    paths: { "twitterWidgets": "//platform.twitter.com/widgets" }
});
define([
	'jquery',
	'plugins',
  'twitterWidgets',
	'dispatcher'
], function($, plugins){
	return plugins["dashboard-twitter-widgets"] = function(config){
		$.dispatcher.on('post-view.rendered-after-/item/source/twitter', function(){
			var self = this;
      window.twttr.widgets.createTweet(
        self.templateData.Meta.id_str,
        self.el.find('.post-content-full').get(0),
        function(){
          self.el.find('.post-core-content').remove();
        },
        { align: 'center', conversation: 'none', cards: 'all' }
      );
		});
	}
});
