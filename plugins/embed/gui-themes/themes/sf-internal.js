'use strict';

define([
    'plugins/button-pagination',
    'plugins/twitter-widgets',
    'plugins/post-hash',
    'plugins/permanent-link',
    'plugins/social-share',
    'plugins/wrappup-toggle',
    'plugins/user-comments',
    'plugins/status',
	'css!theme/liveblog',
	'tmpl!theme/container',
	'tmpl!theme/item/base',
	'tmpl!theme/item/source/youtube',
    'tmpl!theme/plugins/permanent-link',
    'tmpl!theme/plugins/social-share-anchor'
], function() {
	return {
		plugins: [
            'button-pagination',
            'twitter-widgets',
            'permanent-link',
            'social-share',
            'wrappup-toggle',
            'user-comments'
		]
	};
});
