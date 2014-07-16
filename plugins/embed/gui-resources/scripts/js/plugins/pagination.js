'use strict';

define([
    'plugins',
    'lib/utils'
], function(plugins, utils) {
    plugins.pagination = function(config) {
        utils.dispatcher.once('initialize.posts-view', function(view) {

            // Set pagination params
            view.collection.clearPaginationParams();
            if (liveblog.limit) {
                view.collection.syncParams.pagination.limit = parseInt(liveblog.limit, 10);
            }

            view.flags.loadingNextPage = false;

            view.updateNextPageOffset = function() {
                this.collection.syncParams.pagination.offset = this.collection.length;
            };

            view.topPage = function() {
                delete this.collection.syncParams.pagination['order.end'];
                //reset offset to first element
                this.collection.syncParams.pagination.offset = 0;
                return this.collection.fetchPage({reset: true});
            };

            view.nextPage = function() {
                if (this.flags.loadingNextPage || !this.hasNextPage()) {
                    return;
                }
                utils.dispatcher.trigger('loading.posts-view', this);
                this.flags.loadingNextPage = true;

                this.updateNextPageOffset();
                var self = this;
                return this.collection.fetchPage().done(function(data) {
                    self.flags.loadingNextPage = false;
                    utils.dispatcher.trigger('loaded.posts-view', self);
                });
            };

            view.hasNextPage = function() {
                return this.collection.length < this.collection.filterProps.total;
            };

            // True if the blog was accessed through a permanent link to a specific post
            // (ex: http://newspaper.de/very-important-liveblog/?liveblog=78)
            view.hasTopPage = function() {
                if (this.flags.hasTopPage) {
                    return true;
                }
                return false;
            };
        });
    };
    return plugins.pagination;
});
