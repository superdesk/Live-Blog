'use strict';
define([
    'plugins',
    'plugins/ivw',
    'lib/utils'
], function(plugins, ivw, utils) {
    plugins['ivw-refresh'] = function(config) {
        utils.dispatcher.once('initialize.blog-view', function(view) {
            if (utils.isClient) {
                view.$el.on('click', '[data-gimme="posts.pending-message-holder"]', function() {
                    ivw();
                });
            }
        });
    };
    return plugins['ivw-refresh'];
});
