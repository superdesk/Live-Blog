define([
  'plugins/live-dashboard-sliders',
  'plugins/dashboard-twitter-widgets',
	'css!theme/liveblog',
  'css!theme/jquery.bxslider',
  'tmpl!theme/container',
  'tmpl!theme/item/base',
  'tmpl!theme/item/posttype/image',
  'tmpl!theme/item/source/instagram',
  'tmpl!theme/item/source/youtube'
], function(){
	return {
		//enviroments: [ 'mobile', 'desktop', 'quirks' ],
    plugins: ['dashboard-twitter-widgets', 'live-dashboard-sliders']
	}
});
