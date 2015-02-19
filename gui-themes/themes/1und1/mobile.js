'use strict';
require.config({
    paths: {
        'loadClientScriptUrl': '//1und1.superdesk.pro/content/lib/embed/themes/1und1/desktop/vendor/iframeresizer.min'
    }
});
define([
    'plugins/social-share',
    'plugins/post-hash',
    'plugins/button-pagination',
    'plugins/permanent-link',
    'plugins/user-comments',
    'plugins/status',
    'plugins/load-client-script',
    'plugins/twitter-widgets',
    'tmpl!theme/container',
    'tmpl!theme/item/base',
    'tmpl!theme/plugins/social-share-anchor',
    'css!theme/liveblog'
], function() {
    return {
        plugins: [
            'social-share',
            'post-hash',
            'button-pagination',
            'permanent-link',
            'user-comments',
            'status',
            'load-client-script',
            'twitter-widgets'
        ]
    };
});
