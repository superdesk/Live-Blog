define([
  'plugins/twitter-widgets',
  'plugins/live-dashboard-sliders',
	'css!theme/liveblog',
  'css!theme/jquery.bxslider',
  'tmpl!theme/container'
], function(){
	return {
		//enviroments: [ 'mobile', 'desktop', 'quirks' ],
		plugins: ['twitter-widgets', 'live-dashboard-sliders']
	}
});
