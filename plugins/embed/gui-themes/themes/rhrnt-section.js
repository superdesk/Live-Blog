'use strict';

define([
	'plugins/wrappup-toggle',
	'plugins/permanent-link',
	'plugins/twitter-widgets',
	'tmpl!theme/container',
	'tmpl!theme/item/base',
	'css!theme/liveblog'
], function() {
	return {
		plugins: [
			'wrappup-toggle',
			'permanent-link',
			'twitter-widgets'
		]
	};
});
