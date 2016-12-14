'use strict';
define([
    'backbone',
    'plugins',
    'plugins/pagination',
    'dust',
    'lib/utils',
    'tmpl!themeBase/plugins/after-button-pagination',
    'tmpl!themeBase/plugins/before-button-pagination'
], function(Backbone, plugins, paginationPlugin, dust, utils) {
    delete plugins.pagination;
    plugins['button-pagination'] = function(config) {
        paginationPlugin(config);

        utils.dispatcher.once('add-all.posts-view', function(view) {
            var current = view.collection.length,
                data = {};

            dust.renderThemed('themeBase/plugins/before-button-pagination', data, function(err, out) {
                view.$el.before(out);
            });

            if ( view.hasNextPage() ) {
                // view.nextPage().done(function() {
                //     console.log( current, view.collection.models[current] );
                // });

                dust.renderThemed('themeBase/plugins/after-button-pagination', data, function(err, out) {
                    view.$el.after(out);
                });
            }
        });
    };
    return plugins['button-pagination'];
});
