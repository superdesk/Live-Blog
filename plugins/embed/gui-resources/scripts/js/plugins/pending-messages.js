'use strict';

define([
    'lib/gettext',
    'plugins',
    'lib/utils',
    'dust',
    'tmpl!themeBase/item/base',
    'tmpl!themeBase/plugins/pending-items-message'
], function (gt, plugins, utils, dust) {
    plugins.pendingMessages = function (config) {
        var blogView = {};

        utils.dispatcher.once('initialize.blog-view', function(view) {
            // Retain the blog view for future reference
            blogView = view;
        });

        utils.dispatcher.once('after-render.blog-view', function(view) {
            // Add the markup for pending messages
            dust.renderThemed('themeBase/plugins/pending-items-message', {}, function(err, out) {
                view.$('[data-gimme="posts.pending-message-placeholder"]').html(out);
            });
        });

        if (utils.isClient) {
            utils.dispatcher.once('initialize.posts-view', function(view) {
                // Method to pause the auto rendering
                view.pauseAutoRender = function() {
                    this.flags.autoRender = false;
                };
                // Method to resume the auto rendering
                view.resumeAutoRender = function() {
                    this.flags.autoRender = true;
                };
                // Add the click event handler for the new items message
                blogView.$el.on('click', '[data-gimme="posts.pending-message"]', function() {
                    view.renderPending();
                });
            });

            // When the pending posts number is updated, update the pending posts link and
            // show or hide accordingly
            utils.dispatcher.on('update-pending.posts-view', function(view) {
                var message = '',
                pending = view.pendingCounter;
                if (pending > 0) {
                    message = gt.sprintf(gt.ngettext('one new post', '%(count)s new posts', pending), {count: pending});
                }
                blogView.$('[data-gimme="posts.pending-message"]').html(message).toggle(pending > 0);
            });
        }
    };
    return plugins.pendingMessages;
});
