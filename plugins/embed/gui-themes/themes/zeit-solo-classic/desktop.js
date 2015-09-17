'use strict';

define([
    'css!theme/liveblog',
    'plugins/button-pagination',
    'plugins/twitter-widgets',
    'plugins/post-hash',
    'plugins/social-share',
    'tmpl!theme/container',
    'tmpl!theme/item/base'
], function() {
    liveblog.hashmark = '?';
    liveblog.hashaddition = '#livedesk-root';
    return {
        plugins: [
            'button-pagination',
            'twitter-widgets',
            'post-hash',
            'social-share'
        ]
    };
});
