define(['providers'], function(providers) {
	providers.youtube = {
		className: 'big-icon-youtube',	
		tooltip: _('Youtube'),
		init: function() {				
			require(['providers','providers/youtube'], function(providers) {
				providers.youtube.init();
			});
		}
	};
	return providers;
});