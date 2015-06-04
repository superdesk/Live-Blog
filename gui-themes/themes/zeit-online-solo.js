define([
    // 'plugins/scroll-pagination',
    'plugins/button-pagination',
    'plugins/twitter-widgets',
    'plugins/post-hash',
    'plugins/social-share',
    'plugins/status',
    'plugins/wrappup-toggle',
    'css!theme/liveblog',
    'tmpl!theme/container',
    'tmpl!theme/item/base',
    'tmpl!theme/plugins/social-share'
], function(dust, gt, moment) {
    'use strict';

    return {
        plugins: [
            // 'scroll-pagination',
            'button-pagination',
            'twitter-widgets',
            'social-share',
            'status',
            'wrappup-toggle'
        ]
    };
});
