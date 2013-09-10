requirejs.config({
    paths: { "twitterWidgets": "//platform.twitter.com/widgets" }
}); 
define([
	'jquery',
	'plugins',
	'dust',
	'dispatcher',
	'tmpl!themeBase/plugins/twitter-widgets',
	'twitterWidgets'
], function($, plugins, dust){
	return plugins["twitter-widgets"] = function(config){
		$.dispatcher.on('post-view.render-/item/source/twitter', function(){
			var self = this;
			/*!
			 * use the twitter widgets as the template for twitter items
			 */
			self.item = (dust.defined('theme/plugins/twitter-widgets')) ? 
				'theme/plugins/twitter-widgets': 'themeBase/plugins/twitter-widgets';
			/*!
			 * if there is a theme implementation of the twitter item 
			 *    use that item as a base for twitter-widgets.dust
			 */
			self.data["baseTwitter"] = (dust.defined('theme/item/source/twitter')) ? 
				'theme/item/source/twitter': 'themeBase/item/source/twitter';
		});
		$.dispatcher.on('post-view.rendered-after-/item/source/twitter', function(){
			var self = this;
			/*!
			 * Create new tweeter with the loaded widgets
			 * get the twitter id from the meta already processed in the view/post
			 * https://dev.twitter.com/docs/intents/events#createTweet
			 */
			window.twttr.widgets.createTweet(
				self.templateData.Meta.id_str,
				self.el.find('.twitter-widgets').get(0),
				void(0),
				{ cards: 'all' }
			);
		});
	}
});