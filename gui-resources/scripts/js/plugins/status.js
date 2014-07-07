'use strict';
define([
    'backbone',
    'plugins',
    'lib/utils',
    'lib/gettext',
    'moment'
], function(Backbone, plugins, utils, gt, moment) {
    if (utils.isClient) {
        plugins.status = function(config) {
            utils.dispatcher.on('initialize.blog-view', function(view) {
                utils.dispatcher.on('after-poller.blog-model conditional-render.blog-view', function() {
                    var t = gt.sprintf('<time data-update-date="%s">%s</time>', moment().milliseconds(), moment().format(gt.pgettext('moment', 'status-time')));
                    view.$('[data-gimme="blog.status"]').html(gt.sprintf(gt.gettext('updated at %s'), t));
                });
                utils.dispatcher.on('before-poller.blog-model', function() {
                    view.$('[data-gimme="blog.status"]').html(gt.gettext('updating...'));
                });
            });
        };
        return plugins.status;
    }
});
