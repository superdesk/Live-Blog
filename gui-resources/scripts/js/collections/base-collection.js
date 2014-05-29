'use strict';

define([
    'underscore',
    'backbone-custom',
    'lib/backbone/model-collection-common',
    'lib/poller',
    'config/defaultPaginationParams'
], function(_, Backbone, modelCollectionCommon, poller, defaultPaginationParams) {

    return Backbone.Collection.extend(_.extend({

        // Cache collection filter properties:
        // * total: total number of items in the collection, provided by the API.
        //      Different from `this.length`, which is the number of items
        //      in the client side Backbone collection, i.e. number of
        //      items that have been retrieved from the API, not total number of
        //      existant items.
        filterProps: {
            total: 0
        },

        // Reset `syncParams.pagination` to the default pagination params.
        clearPaginationParams: function() {
            var defParams = this.defaultPaginationParams || defaultPaginationParams;
            this.syncParams.pagination = _.extend(this.syncParams.pagination,
                                                                    defParams);
        },

        // Request a whole page of collection items.
        // Set pagination params in `this.syncParams.pagination`.
        fetchPage: function(options) {
            options            = options || {};
            var paginationOpts = this.syncParams.pagination || {};
            options.data       = _.extend(paginationOpts, options.data);
            return this.fetch(options);
        },

        // Request for updates on the collection.
        // Set update params in `this.syncParams.updates`.
        fetchUpdates: function(options) {
            options         = options || {};
            var updatesOpts = this.syncParams.updates || {};
            options.data    = _.extend(updatesOpts, options.data);
            return this.fetch(options);
        },

        // The function to be called for polling.
        poller: function(options) {
            this.fetchUpdates(options);
        }

    }, modelCollectionCommon, poller));
});
