'use strict';

define([
    'underscore',
    'models/base-model',
    'collections/posts',
    'lib/utils'
], function(_, BaseModel, Posts, utils) {

    return BaseModel.extend({

        syncParams: {
            headers: {
                'X-Filter': 'Description, Title, EmbedConfig, Language.Code'
            },
            updates: {}
        },

        pollInterval: 10000,

        urlRoot: function() {
            return liveblog.servers.rest + '/resources/LiveDesk/Blog/';
        },

        initialize: function() {
            this.set('publishedPosts', new Posts([], {blogId: this.id}));
            if (utils.isClient) {
                this.startPolling();
            }
        },

        // The function to be called for polling.
        poller: function(options) {
            delete options.data;
            var self = this,
                dfd;
            utils.dispatcher.trigger('before-poller.blog-model', self);
            dfd = this.fetch(options);
            if (_.has(dfd, 'done')) {
                dfd.done(function() {
                    utils.dispatcher.trigger('after-poller.blog-model', self);
                });
            }
        },

        parse: function(data) {
            if (_.isString(data.EmbedConfig)) {
                data.EmbedConfig = JSON.parse(data.EmbedConfig);
            }
            if (_.isUndefined(data.EmbedConfig)) {
                data.EmbedConfig = {};
            }
            return data;
        }
    });
});
