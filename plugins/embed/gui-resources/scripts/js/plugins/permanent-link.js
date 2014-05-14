'use strict';
define([
    'plugins',
    'lib/utils',
    'dust',
    'lib/helpers/visibility-toggle',
    'tmpl!themeBase/item/base',
    'tmpl!themeBase/plugins/permanent-link'
], function (plugins, utils, dust, visibilityToggle) {
    if (utils.isClient) {
        plugins.permalink = function (config) {
            utils.dispatcher.on('after-render.post-view', function(view) {
                 //add the 'anchor' to the template
                dust.renderThemed('themeBase/plugins/permanent-link', {}, function(err, out) {
                    view.$('[data-gimme="post.permanent-link-placeholder"]').html(out);
                });
                var permLink = '';
                if (view.permalink && typeof view.permalink === 'function') {
                    permLink = view.permalink();
                    view.$('[data-gimme="post.share-permalink"]').val(permLink);
                }
            });
            utils.dispatcher.on('initialize.post-view', function (view) {
                view.clientEvents({
                    'click [data-gimme="post.permalink"]': 'permalinkAction'
                });
                //toggle the visibility of the permalink input box
                view.permalinkAction = function (evt) {
                    evt.preventDefault();
                    var box = this.$(evt.target).siblings('[data-gimme="post.share-permalink"]');
                    if (visibilityToggle(box)) {
                        var postShare = this.$('[data-gimme^="post.share"][data-gimme!="post.share-permalink"]');
                        visibilityToggle(postShare, false);
                        box.trigger('focus');
                    }
                };

                //select all the content of the permalink input box for easy copying
                view.clientEvents({
                    'click [data-gimme="post.share-permalink"]': 'permalinkInput',
                    'focus [data-gimme="post.share-permalink"]': 'permalinkInput'
                });
                view.permalinkInput = function (evt) {
                    view.$(evt.target).select();
                };
                view.delegateEvents();
            });
        };
        return plugins.permalink;
    }
});
