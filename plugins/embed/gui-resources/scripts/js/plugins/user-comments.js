'use strict';
/*jshint unused: false */
define([
    'plugins',
    'plugins/user-comments-popup',
    'lib/utils',
    'dust',
    'lib/helpers/display-toggle',
    'tmpl!themeBase/plugins/user-comment-message',
    'tmpl!themeBase/plugins/user-comment-backdrop',
    'tmpl!themeBase/plugins/user-comment-action',
    'tmpl!themeBase/plugins/user-comment'
], function (plugins, UserCommentsPopupView, utils, dust, displayToggle) {
    plugins['user-comments'] = function (config) {
        //on blog config update show or hide the comment link
        utils.dispatcher.on('config-update.blog-view', function (view) {
            displayToggle(view.$('[data-gimme="blog.comment"]'),
                view.model.get('EmbedConfig').UserComments);
        });
        //after the blog is rendered
        utils.dispatcher.on('conditional-render.blog-view', function (view) {
            //add the comment link in the blog theme
            dust.renderThemed('themeBase/plugins/user-comment-action', {UserComments: view.model.get('EmbedConfig').UserComments}, function(err, out) {
                view.$('[data-gimme="blog.comment-action"]').html(out);
            });
            displayToggle(view.$('[data-gimme="blog.comment"]'), config.UserComments);
            //add the comment form
            dust.renderThemed('themeBase/plugins/user-comment', {}, function(err, out) {
                view.$('[data-gimme="blog.comment-box"]').html(out);
            });
            //add the after submit message box
            dust.renderThemed('themeBase/plugins/user-comment-message', {}, function(err, out) {
                view.$('[data-gimme="blog.comment-box-message"]').html(out);
            });
            //add the comment backdropt
            dust.renderThemed('themeBase/plugins/user-comment-backdrop', {}, function(err, out) {
                view.$('[data-gimme="blog.comment-box-backdrop"]').html(out);
            });
            //create the comment popup view that will handle all the actions
            if (utils.isClient) {
                var popupView = new UserCommentsPopupView({
                    el: view.el,
                    blogview: view,
                    model: view.model
                });
            }
        });
    };
    return plugins['user-comments'];
});
