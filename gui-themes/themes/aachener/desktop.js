'use strict';
require.config({
    paths: {
        'typekitFont': '//use.typekit.net/oal1wjf'
    }
});
define([
    'css!theme/liveblog',
    'plugins/button-pagination',
    'plugins/twitter-widgets',
    'plugins/post-hash',
    'plugins/permanent-link',
    'plugins/social-share',
    'plugins/wrappup-toggle',
    'plugins/user-comments',
    'plugins/status',
    'plugins/typekit',
    'plugins/image-fix',
    'tmpl!theme/plugins/permanent-link',
    'tmpl!theme/container',
    'tmpl!theme/item/base'
], function($) {
    return {
        plugins: [
            'button-pagination',
            'twitter-widgets',
            'post-hash',
            'permanent-link',
            'social-share',
            'wrappup-toggle',
            'user-comments',
            'status',
            'typekit'
        ]
    };
});
