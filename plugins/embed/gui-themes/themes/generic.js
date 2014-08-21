define([
    'plugins/status',
    'plugins/social-share',
    'plugins/post-hash',
    'plugins/wrappup-toggle',
    'plugins/scroll-pagination',
    'plugins/permanent-link',
    'plugins/user-comments',
    'plugins/twitter-widgets',
    'tmpl!theme/item/base',
    'css!theme/liveblog'
], function() {
    'use strict';
    return {
        plugins: [  'status',
                    'social-share',
                    'post-hash',
                    'wrappup-toggle',
                    'scroll-pagination',
                    'permanent-link',
                    'user-comments',
                    'twitter-widgets']
    };
});
