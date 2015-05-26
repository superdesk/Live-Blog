'use strict';

define([
    'css!theme/liveblog',
    'plugins/button-pagination',
    'plugins/twitter-widgets',
    'plugins/post-hash',
    'plugins/social-share',
    'plugins/predefined-types',
    'tmpl!theme/container',
    'tmpl!theme/item/base',
    'tmpl!theme/item/predefined/scorecard'
], function() {
    return {
        plugins: [
            'button-pagination',
            'twitter-widgets',
            'post-hash',
            'social-share',
            'predefined-types'
        ]
    };
});
