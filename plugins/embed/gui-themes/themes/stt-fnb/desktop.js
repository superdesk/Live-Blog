'use strict';

define([
    'css!theme/liveblog',
    'plugins/scroll-pagination',
    'plugins/twitter-widgets',
    'plugins/post-hash',
    'plugins/permanent-link',
    'plugins/social-share',
    'plugins/wrappup-toggle',
    'plugins/user-comments',
    'tmpl!theme/container',
    'tmpl!theme/item/base'
], function() {
    return {
        plugins: [
            'scroll-pagination',
            'twitter-widgets',
            'post-hash',
            'permanent-link',
            'social-share',
            'wrappup-toggle',
            'user-comments'
        ]
    };
});
