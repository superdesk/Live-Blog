'use strict';

define([
    'css!theme/liveblog',
    'plugins/button-pagination',
    'plugins/twitter-widgets',
    'plugins/post-hash',
    'tmpl!theme/container',
    'tmpl!theme/item/base'
], function() {
    return {
        plugins: [
            'button-pagination',
            'twitter-widgets',
            'post-hash'
        ]
    };
});
