define([
    'plugins/post-hash',
    'plugins/status',
    'plugins/predefined-types',
    'theme/scripts/js/plugins/ampify',
    'theme/scripts/js/plugins/button-pagination',
    'theme/scripts/js/plugins/social-share',
    // 'css!theme/liveblog',
    'tmpl!theme/container',
    'tmpl!theme/posts-list',
    'tmpl!theme/item/base',
    // 'tmpl!theme/item/posttype/image',
    'tmpl!theme/item/predefined/scorecard',
    'tmpl!theme/item/source/flickr',
    'tmpl!theme/item/source/google/images',
    'tmpl!theme/item/source/google/news',
    'tmpl!theme/item/source/google/web',
    'tmpl!theme/item/source/instagram',
    'tmpl!theme/item/source/twitter',
    'tmpl!theme/item/source/youtube',
    'tmpl!theme/plugins/after-button-pagination',
    'tmpl!theme/plugins/before-button-pagination',
    'tmpl!theme/plugins/social-share'
], function() {
    'use strict';
    liveblog.hashmark = '?';
    liveblog.hashaddition = '#livedesk-root';
    return {
        plugins: [
            'ampify',
            'button-pagination',
            'social-share',
            'status'
        ]
    };
});
