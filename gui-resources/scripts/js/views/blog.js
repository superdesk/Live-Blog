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

        el: false,

        initialize: function() {
            utils.dispatcher.trigger('initialize.blog-view', this);

            this.setTemplate('themeBase/container');

            this.listenTo(this.model, 'change', this.update);
            this.listenTo(this.model, 'update', function() {
                console.log('model update');
            });

            // When creating the PostsView, if there is server side generated HTML
            // attach the view to it
            var collection      = this.model.get('publishedPosts'),
                postsViewSel    = PostsView.prototype.rootSel,
                postsViewRootEl = this.$(postsViewSel);
            if (utils.isClient && postsViewRootEl.length !== 0) {
                var postsView = new PostsView({collection: collection, el: postsViewSel});
                this.setView('[data-gimme="posts.view"]', postsView);
            } else {
                this.setView('[data-gimme="posts.view"]', new PostsView({collection: collection}));
            }
        },
        conditionalRender: function() {
            // if there is no previous generated HTML markup, render the view
            if (this.$el.is(':empty')) {
                this.render();
            // if the markup is already there, use it
            } else {
                //make sure that we update the seo generated markup with the latest changes
                this.update();
            }
            utils.dispatcher.trigger('conditional-render.blog-view', this);
        },
        afterRender: function() {
            utils.dispatcher.trigger('after-render.blog-view', this);
        },
        beforeRender: function() {
            utils.dispatcher.trigger('before-render.blog-view', this);
        },
        update: function() {
            var embedConfig = {};
            embedConfig = this.model.get('EmbedConfig');
            //Show or hide the entire advertisment
            if (!_.isUndefined(embedConfig.MediaToggle)) {
                displayToggle(this.$('[data-gimme="blog.media-toggle"]'), embedConfig.MediaToggle);
            }
            //Set the target and the image for the advertisment
            if (embedConfig.MediaUrl) {
                this.$('[data-gimme="blog.media-url"]').attr('href', embedConfig.MediaUrl);
            }
            if (embedConfig.MediaImage) {
                this.$('[data-gimme="blog.media-image"]').attr('src', embedConfig.MediaImage);
            }
            //Set title and description
            this.$('[data-gimme="blog.title"]').html(this.model.get('Title'));
            this.$('[data-gimme="blog.description"]').html(this.model.get('Description'));
            //Trigger update config
            if (!_.isEmpty(embedConfig)) {
                utils.dispatcher.trigger('config-update.blog-view', this);
            }
        },
        serialize: function() {
            return this.model.toJSON();
        },
        // methods visible for plugins to control the poller mechanics.
        stopPoller: function() {
            this.model.stopPolling();
            this.model.get('publishedPosts').stopPolling();
        },
        starPoller: function() {
            this.model.startPolling();
            this.model.get('publishedPosts').startPolling();
        }
    });
});
