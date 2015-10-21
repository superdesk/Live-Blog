define([
    'plugins/social-share',
    'plugins/post-hash',
    'plugins/button-pagination',
    'plugins/permanent-link',
    'plugins/user-comments',
    'plugins/twitter-widgets',
    'tmpl!theme/container',
    'tmpl!theme/item/base',
    'css!theme/liveblog'
], function() {
    'use strict';
    return {
        plugins: [
            'social-share',
            'post-hash',
            'button-pagination',
            'permanent-link',
            'user-comments',
            'twitter-widgets'
        ]
    };
});
