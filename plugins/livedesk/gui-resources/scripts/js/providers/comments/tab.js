define([ 'providers' ], function( providers ) {
	providers.comments = {
		className: 'big-icon-sms',
		tooltip: _('User Comments source'),
		init: function(theBlog) {
			var args = arguments;
			require([ 'providers', 'providers/comments' ], function( providers ) {
				providers.comments.init(args);
			});
		}
	};
	return providers;
});