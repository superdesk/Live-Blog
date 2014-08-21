'use strict';

define([
    'css!theme/liveblog',
    'plugins/button-pagination',
    'plugins/twitter-widgets',
    'plugins/post-hash',
    'plugins/social-share',
    'plugins/ivw-counter',
    'tmpl!theme/container',
    'tmpl!theme/item/base'
], function() {
    return {
        plugins: [
            'button-pagination',
            'twitter-widgets',
            'post-hash',
            'social-share',
            'ivw-counter'
        ]
    };
});
