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

        utils.dispatcher.once('after-render.blog-view', function(view) {
            var data = {},
                postsView = view.getView('[data-gimme="posts.view"]');

            dust.renderThemed('themeBase/plugins/before-button-pagination', data, function(err, out) {
                view.$el.find('#zon-live-list').prepend(Backbone.$(out));
            });

            if (postsView.hasNextPage()) {
                var lastOrder = parseFloat(postsView.collection.models[postsView.collection.models.length - 1].get('Order'));
                data.lastPermalink = '?liveblog.item.id=' + lastOrder + '#livedesk-root';
                dust.renderThemed('themeBase/plugins/after-button-pagination', data, function(err, out) {
                    view.$el.find('#zon-live-list').append(Backbone.$(out));
                });
            }
        });
    };
    return plugins['button-pagination'];
});
