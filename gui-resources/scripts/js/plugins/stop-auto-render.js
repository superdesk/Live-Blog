'use strict';

define([
    'lib/utils',
    'plugins'
], function (utils, plugins) {
    plugins.stopAutoRender = function (config) {
        if (utils.isClient) {
            utils.dispatcher.once('initialize.posts-view', function(view) {
                view.flags.autoRender = false;
            });
        }
    };
    return plugins.stopAutoRender;
});
