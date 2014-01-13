define([ 'providers' ], function( providers ) {
	providers.sms = {
		className: 'big-icon-sms',
		tooltip: _('Sms source'),
		init: function(theBlog) {
			require([ 'providers', 'providers/sms' ], function( providers ) {
				providers.sms.init(theBlog);
			});
		}
	};
	return providers;
});