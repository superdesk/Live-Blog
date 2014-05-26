'use strict';

define([
    'css!theme/liveblog',
    'plugins/button-pagination',
    'plugins/twitter-widgets',
    'plugins/permanent-link',
    'plugins/social-share',
    'plugins/wrappup-toggle',
    'plugins/user-comments',
    'tmpl!theme/container',
    'tmpl!theme/item/base'
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
