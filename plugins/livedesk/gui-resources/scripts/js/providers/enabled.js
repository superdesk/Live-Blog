define('providers/enabled', [
    'order!providers/edit/tab',
    'order!providers/colabs/tab',
	'order!providers/google/tab',
	'order!providers/twitter/tab',
	'order!providers/flickr/tab',
    'order!providers/youtube/tab',
	'order!providers/instagram/tab',
    'order!providers/soundcloud/tab',
	'order!providers/ads/tab',
], function(providers){ return providers; });
