define([ 'providers' ], function( providers ) {
	providers.flickr = {
		className: 'big-icon-flickr',
		tooltip: _('Flickr'),
		init: function() {
			require([ 'providers', 'providers/flickr' ], function( providers ) {
				providers.flickr.init();
			});
		}
	};
	return providers;
});