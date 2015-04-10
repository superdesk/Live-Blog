'use strict';

define([
    'css!theme/liveblog',
    'plugins/scroll-pagination-always',
    'plugins/twitter-widgets',
    'plugins/post-hash',
    'plugins/permanent-link',
    'plugins/social-share',
    'plugins/wrappup-toggle',
    'plugins/user-comments'
], function() {
    return {
        plugins: [
            'scroll-pagination-always',
            'twitter-widgets',
            'permanent-link',
            'social-share',
            'wrappup-toggle',
            'user-comments'
        ]
    };
});
