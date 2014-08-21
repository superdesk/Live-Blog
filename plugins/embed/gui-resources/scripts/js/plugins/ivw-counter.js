'use strict';
define([
    'plugins',
    'plugins/button-pagination',
    'plugins/ivw',
    'lib/utils'
], function(plugins, buttonPaginationPlugin, ivw, utils) {
    delete plugins['button-pagination'];
    plugins['ivw-counter'] = function(config) {
        buttonPaginationPlugin(config);
        utils.dispatcher.once('initialize.posts-view', function(view) {
            view.clientEvents({'click [data-gimme="posts.nextPage"]': 'ivwCounter'});
            view.ivwCounter = function() {
                view.buttonNextPage();
                ivw();
            };
        });
    };
    return plugins['ivw-counter'];
});
