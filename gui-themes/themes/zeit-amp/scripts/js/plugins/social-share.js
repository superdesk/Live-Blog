/* jshint maxparams: 9 */
'use strict';

define([
    'backbone',
    'underscore',
    'plugins',
    'lib/utils',
    'dust',
    'tmpl!themeBase/plugins/social-share'
], function(Backbone, _, plugins, utils, dust) {

    plugins['social-share'] = function(config) {

        utils.dispatcher.on('after-render.post-view', function(view) {
            // Add social share links to the view
            var blog = view.parentView().parentView().model,
                data = {
                    title: blog.get('Title')
                };

            if (view.permalink && typeof view.permalink === 'function') {
                data.permalink = view.permalink();
            }

            dust.renderThemed('themeBase/plugins/social-share', data, function(err, out) {
                view.$('[data-gimme="post.social-share-placeholder"]').html(out);
            });
        });
    };
});
