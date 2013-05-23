define([ 'providers' ], function( providers ) {
	providers.soundcloud = {
		className: 'big-icon-soundcloud',
		tooltip: _('Soundcloud'),
		init: function() {
			require([ 'providers', 'providers/soundcloud' ], function( providers ) {
				providers.soundcloud.init();
			});
		}
	};
	return providers;
});