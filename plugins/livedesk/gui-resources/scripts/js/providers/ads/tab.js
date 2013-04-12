define([ 'providers' ], function( providers ) {
	providers.ads = {
		className: 'big-icon-ads',       
		tooltip: _('Advertisment'),
		init: function() {
			var args = arguments;
			require(['providers','providers/ads'], function(providers){ 
				providers.ads.init.apply(providers.ads, args); 
			});
		}
	};
	return providers;
});