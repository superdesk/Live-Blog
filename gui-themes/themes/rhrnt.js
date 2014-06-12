'use strict';

define([
	'plugins/wrappup-toggle',
	'plugins/permanent-link',
	'plugins/user-comments',
	'plugins/twitter-widgets',
	'plugins/social-share',
	'tmpl!theme/container',
	'tmpl!theme/item/base',
	'css!theme/liveblog'
], function() {
	return {
		plugins: [
			'wrappup-toggle',
			'permanent-link',
			'user-comments',
			'twitter-widgets',
			'social-share'
		]
	};
});
