'use strict';

define([
    'views/base-view',
    'views/posts',
    'lib/utils',
    'lib/helpers/display-toggle',
    'underscore',
    'tmpl!themeBase/container'
], function(BaseView, PostsView, utils, displayToggle, _) {

    return BaseView.extend({

        // Set `el` to the top level element from the template
        // instead of the default behaviour of inserting a `div` element
        // (Backbone.LayoutManager).
        el: false,

        initialize: function() {
            utils.dispatcher.trigger('initialize.blog-view', this);

            this.setTemplate('themeBase/container');

            this.listenTo(this.model, 'change', this.update);

            // Add `PostsView` as a nested view.
            var collection      = this.model.get('publishedPosts'),
                postsViewSel    = PostsView.prototype.rootSel,
                postsViewRootEl = this.$(postsViewSel);

            if (utils.isClient && postsViewRootEl.length !== 0) {
                // If there is server side generated HTML in the page when the `PostsView`
                // is created client side, attach the view to it.
                var postsView = new PostsView({collection: collection, el: postsViewSel});
                this.setView('[data-gimme="posts.view"]', postsView);
            } else {
                this.setView('[data-gimme="posts.view"]', new PostsView({collection: collection}));
            }
        },

        conditionalRender: function() {
            // If there is no previous generated HTML markup, render the view.
            if (this.$el.is(':empty')) {
                this.render();
            // If the markup is already there, use it.
            } else {
                // Make sure that the server side generated markup gets
                // updated with the latest changes.
                this.update();
            }
            utils.dispatcher.trigger('conditional-render.blog-view', this);
        },

        // Backbone.LayoutManager `afterRender`.
        afterRender: function() {
            utils.dispatcher.trigger('after-render.blog-view', this);
        },

        // Backbone.LayoutManager `beforeRender`.
        beforeRender: function() {
            utils.dispatcher.trigger('before-render.blog-view', this);
        },

        update: function() {
            var embedConfig = this.model.get('EmbedConfig') || {};

            // Show or hide the entire advertisement block.
            if (!_.isUndefined(embedConfig.MediaToggle)) {
                displayToggle(this.$('[data-gimme="blog.media-toggle"]'), embedConfig.MediaToggle);
            }

            // Set the target and image for the advertisement block.
            if (embedConfig.MediaUrl) {
                this.$('[data-gimme="blog.media-url"]').attr('href', embedConfig.MediaUrl);
            }
            if (embedConfig.MediaImage) {
                this.$('[data-gimme="blog.media-image"]').attr('src', embedConfig.MediaImage);
            }

            // Set blog title and description.
            this.$('[data-gimme="blog.title"]').html(this.model.get('Title'));
            this.$('[data-gimme="blog.description"]').html(this.model.get('Description'));

            // Trigger update config.
            if (!_.isEmpty(embedConfig)) {
                utils.dispatcher.trigger('config-update.blog-view', this);
            }
        },

        // Backbone.LayoutManager `serialize`.
        serialize: function() {
            return this.model.toJSON();
        },

        // Method visible to plugins for stopping polling for updates.
        stopPoller: function() {
            this.model.stopPolling();
            this.model.get('publishedPosts').stopPolling();
        },

        // Method visible to plugins for starting polling for updates.
        starPoller: function() {
            this.model.startPolling();
            this.model.get('publishedPosts').startPolling();
        }
    });
});
