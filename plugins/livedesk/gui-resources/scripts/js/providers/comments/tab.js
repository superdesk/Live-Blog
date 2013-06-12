define([ 'providers' ], function( providers ) {
	providers.comments = {
		className: 'big-icon-usercomments',
		tooltip: _('Comments'),
		init: function(theBlog) {
			var args = arguments;
			require([ 'providers', 'providers/comments' ], function( providers ) {
				providers.comments.init(args);
			});
		}
	};
	return providers;
});