'use strict';

define([
    'plugins',
    'plugins/button-pagination',
    'plugins/pending-messages',
    'config/scroll-pagination-plugin',
    'lib/utils'
], function(plugins, buttonPaginationPlugin, pendingMessagesPlugin, pluginConfig, utils) {
    delete plugins['button-pagination'];
    delete plugins['pending-messages'];

    plugins['scroll-pagination'] = function(config) {

        buttonPaginationPlugin(config);
        pendingMessagesPlugin(config);

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

            require(['waypoints'], function() {
                utils.dispatcher.on('pagination-next-updated.posts-view', function(view) {
                    // After updating pagination buttons, add a waypoint for
                    // showing the next page on scroll (if there are any)
                    if (view.hasNextPage()) {
                        addBottomWaypoint(view, view.$('[data-gimme="posts.nextPage"]'));
                    }
                });
                utils.dispatcher.once('pagination-next-updated.posts-view', function(view) {
                    // Add a waypoint for detecting scrolling down
                    addTopScrollDownWaypoint(view);
                });
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
            nextPageButton.waypoint(function() {
                view.buttonNextPage();
            }, {
                continuous: false, // Fire ALL waypoints triggered in one scroll
                triggerOnce: true,
                offset: '100%',
                context: view.el
            });
        };

        // When user starts scrolling down, deactivate auto render of new posts
        // and add a waypoint for detecting when the user scroll backs to the top
        var addTopScrollDownWaypoint = function(view) {
            // Use the "before page" button (always at the top of the posts list) to
            // detect the user scrolling down
            var beforePageButton = view.$('[data-gimme="posts.beforePage"]');
            beforePageButton.waypoint(function(direction) {
                if (direction === 'down') {
                    view.pauseAutoRender();
                    // Destroy the waypoint to prevent it for being fired several
                    // times while the user scrolls down
                    beforePageButton.waypoint('destroy');
                    addTopScrollUpWaypoint(view);
                }
            },
            {
                continuous: false,
                offset: pluginConfig.nextPageTriggerOffset,
                context: view.el
            });
        };

        // When user comes back to the top of the list, render pending posts,
        // enable auto rendering and add a waypoint for detecting the user scrolling down
        var addTopScrollUpWaypoint = function(view) {
            var firstPost = view.firstPost().$el;
            firstPost.waypoint(function(direction) {
                if (direction === 'up') {
                    view.renderPending();
                    view.resumeAutoRender();
                    // Destroy waypoint once fired while going up
                    firstPost.waypoint('destroy');
                    addTopScrollDownWaypoint(view);
                }
            }, {
                continuous: false,
                offset: -1, // Using -1 because with offset 0, the waypoint is not triggered
                context: view.el
            });
        };
    };

    return plugins['scroll-pagination'];
});
