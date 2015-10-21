'use strict';

define([
    'plugins',
    'plugins/button-pagination',
    'config/scroll-pagination-plugin',
    'lib/utils'
], function(plugins, buttonPaginationPlugin, pluginConfig, utils) {
    delete plugins['button-pagination'];
    delete plugins['pending-messages'];

    plugins['scroll-pagination-always'] = function(config) {

        buttonPaginationPlugin(config);

        // Set the scroll for the posts list box
        utils.dispatcher.once('add-all.posts-view', function(view) {
            view.$el.
                css('overflow-y', 'auto').
                css('overflow-x', 'auto').
                css('height', pluginConfig.scrollHeight + 'px');
        });

        if (utils.isClient) {
            // Add event for "To Top" button, for coming back to the top of the posts list
            utils.dispatcher.on('initialize.blog-view', function(view) {
                activateToTopButton(view);
            });

            // require(['waypoints'], function() {
            // });
            utils.dispatcher.on('pagination-next-updated.posts-view', function(view) {
                // After updating pagination buttons, add a waypoint for
                // showing the next page on scroll (if there are any)
                if (view.hasNextPage()) {
                    addBottomWaypoint(view, view.$('[data-gimme="posts.nextPage"]'));
                }
            });
        }

        var activateToTopButton = function(postsView) {
            postsView.clientEvents({
                'click [data-gimme="posts.to-top"]':          'toTop',
                'click [data-gimme="posts.pending-message"]': 'toTop'
            });

            postsView.toTop = function(e) {
                e.preventDefault();
                this.$('[data-gimme="posts.list"]').scrollTop(0);
            };
        };

        // When scroll reachs the "load more" button, render next page
        var addBottomWaypoint = function(view, nextPageButton) {
            require(['waypoints'], function() {
                nextPageButton.waypoint(function() {
                    view.buttonNextPage();
                }, {
                    continuous: false, // Fire ALL waypoints triggered in one scroll
                    triggerOnce: true,
                    offset: '100%',
                    context: view.el
                });
            });
        };

    };

    return plugins['scroll-pagination-always'];
});
