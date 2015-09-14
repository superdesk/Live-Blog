define([
    // 'plugins/scroll-pagination',
    'plugins/button-pagination',
    'plugins/twitter-widgets',
    'plugins/post-hash',
    'plugins/social-share',
    'plugins/status',
    'plugins/wrappup-toggle',
    'plugins/predefined-types',
    'css!theme/liveblog',
    'tmpl!theme/container',
    'tmpl!theme/item/base',
    'tmpl!theme/plugins/social-share',
    'tmpl!theme/item/predefined/scorecard'
], function(dust, gt, moment) {
    'use strict';
    liveblog.hashmark = '?';
    liveblog.hashaddition = '#livedesk-root';
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
