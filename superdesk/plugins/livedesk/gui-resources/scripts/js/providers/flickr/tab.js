define('providers/flickr/tab', ['providers'], function(providers) {
	providers.flickr = {
		className: 'big-icon-flickr',		
		init: function() {				
			require(['providers','providers/flickr'], function(providers) {
				providers.flickr.init();
			});
		}
	};
	return providers;
});