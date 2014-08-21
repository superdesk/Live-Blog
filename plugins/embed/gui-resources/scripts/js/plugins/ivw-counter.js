'use strict';
define([
    'plugins',
    'plugins/button-pagination',
    'lib/utils'
], function(plugins, buttonPaginationPlugin, utils) {
    delete plugins['button-pagination'];
    plugins['ivw-counter'] = function(config) {
        buttonPaginationPlugin(config);
        utils.dispatcher.once('initialize.posts-view', function(view) {
            view.clientEvents({'click [data-gimme="posts.nextPage"]': 'ivwCounter'});
            view.ivwCounter = function() {
                /* global RPO */
                view.buttonNextPage();
                if ((typeof(RPO) !== 'undefined') && RPO.reloadIVW) {
                    RPO.reloadIVW();
                }
            };
        });
    };
    return plugins['ivw-counter'];
});
