'use strict';
define([
    'jquery',
    'plugins',
    'plugins/button-pagination',
], function($, plugins, buttonPaginationPlugin) {
    delete plugins['button-pagination'];
    plugins['ivw-counter'] = function(config) {
        buttonPaginationPlugin(config);
        $.dispatcher.on('class.posts-view', function() {
            var view = this.prototype;
            view.events['[data-gimme="posts.nextPage"]'] = { 'click': "ivwCounter" }
            view.ivwCounter = function(evt) {
                RPO.reloadIVW();
            };
        });
    };
    return plugins['ivw-counter'];
});
