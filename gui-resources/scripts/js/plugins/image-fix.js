'use strict';

define([
    'lib/utils',
    'plugins'
], function (utils, plugins) {
    plugins.imageFix = function (config) {
        utils.dispatcher.on('before-render.post-view', function (view) {
            if (view.model.get('item') !== 'posttype/image' &&
                view.model.get('item') !== 'posttype/normal') {
                return;
            }
            var Content = view.model.get('Content');
            // remove 'null' with or without &nbsp; trailing.
            Content = Content.replace(/null(\n&nbsp;)?/, '');
            // replace all links that have images with the actuall image.
            Content = Content.replace(new RegExp('<a([^>]*)>(.*?)</a>', 'gi'), function(all, attr) {
                attr.replace(/"(.*?)content\/media_archive\/image([^"]*)"/, function(link) {
                    all = '<img src=' + link + '>';
                });
                return all;
            });
            // add a class for all local images.
            Content = Content.replace(/"(.*?)content\/media_archive\/image([^"]*)"/, function(link) {
                return link + ' class="liveblog-local"';
            });
            view.model.set({Content: Content}, {silent: true});
        });

    };
    return plugins.imageFix;
});
