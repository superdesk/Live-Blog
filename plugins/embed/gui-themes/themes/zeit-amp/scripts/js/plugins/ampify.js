define([
    'plugins',
    'lib/utils',
    'dust'
], function(plugins, utils, dust) {
    'use strict';

    plugins.ampify = function(config) {

        utils.dispatcher.on('after-render.post-view', function(view) {
            view.$('*[style]').removeAttr('style');

            switch (view.$el.attr('class')) {
                case 'link':
                    var icon = view.$('.source-icon img, .source-icon amp-img');
                    icon.replaceWith('<amp-img src="' + icon.attr('src') + '" width="16" height="16" layout="fixed"></amp-img>');
                    break;
            }

            var images = view.$('img'),
                img,
                index;

            for (index = images.length; index--;) {
                // @TODO get width and height of image if missing
                img = images.eq(index);
                if (img.attr('width') && img.attr('height')) {
                    img.replaceWith('<amp-img src="' + img.attr('src') + '" width="' + img.attr('width') + '" height="' + img.attr('height') + '" layout="responsive"></amp-img>');
                }
            }
        });
    };
});