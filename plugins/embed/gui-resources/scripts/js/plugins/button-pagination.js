'use strict';
define([
    'backbone',
    'plugins',
    'plugins/pagination',
    'dust',
    'lib/utils',
    'lib/helpers/display-toggle',
    'tmpl!themeBase/item/base',
    'tmpl!themeBase/plugins/after-button-pagination',
    'tmpl!themeBase/plugins/before-button-pagination'
], function(Backbone, plugins, paginationPlugin, dust, utils, displayToggle) {
    delete plugins.pagination;
    plugins['button-pagination'] = function(config) {
        paginationPlugin(config);

        utils.dispatcher.on('initialize.blog-view', function(view) {

            view.clientEvents({'click [data-gimme="posts.to-top"]': 'toTop'});
            view.toTop = function(evt) {
                var self = this,
                new_position = self.el.offset();
                window.scrollTo(new_position.left, new_position.top);
            };
        });

        utils.dispatcher.once('add-all.posts-view', function(view) {
            var data = {};
            data.baseItem = dust.themed('themeBase/item/base');
            if (view.$('[data-gimme="posts.beforePage"]').length === 0) {
                dust.renderThemed('themeBase/plugins/before-button-pagination', data, function(err, out) {
                    var  el = Backbone.$(out);
                    displayToggle(el, false);
                    view.$el.prepend(el);
                });
            }
            if (view.$('[data-gimme="posts.nextPage"]').length === 0) {
                dust.renderThemed('themeBase/plugins/after-button-pagination', data, function(err, out) {
                    var  el = Backbone.$(out);
                    displayToggle(el, false);
                    view.$el.append(el);
                });
            }
        });

        utils.dispatcher.once('add-all.posts-view', function(view) {
            view.checkNextPage();
            view.checkTopPage();
        });

        utils.dispatcher.once('initialize.posts-view', function(view) {
            view.clientEvents({
                'click [data-gimme="posts.nextPage"]': 'buttonNextPage',
                'click [data-gimme="posts.beforePage"]': 'buttonTopPage'
            });

            view.checkTopPage = function(evt) {
                displayToggle(this.$('[data-gimme="posts.beforePage"]'), this.hasTopPage());
            };
            view.checkNextPage = function(evt) {
                displayToggle(this.$('[data-gimme="posts.nextPage"]'), this.hasNextPage());
            };

            view.buttonNextPage = function(evt) {
                view.flags.buttonNextPage = true;
                var item = view.$('[data-gimme="posts.nextPage"]');
                item.addClass('loading');
                view.nextPage().done(function() {
                    view.flags.buttonNextPage = false;
                    item.removeClass('loading');
                    view.checkNextPage();
                });
            };

            view.buttonTopPage = function(evt) {

                var item = view.$('[data-gimme="posts.beforePage"]');
                item.addClass('loading');
                view.flags.topPage = false;
                view.topPage().done(function() {
                    item.removeClass('loading');
                    displayToggle(item, false);
                    view.checkNextPage();
                });

            };
        });
    };
    return plugins['button-pagination'];
});
