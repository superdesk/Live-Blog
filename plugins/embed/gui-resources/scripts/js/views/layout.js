/* jshint maxparams: 8 */
'use strict';

define([
    'underscore',
    'views/base-view',
    'views/blog',
    'views/embed-code',
    'models/blog',
    'models/liveblog',
    'load-theme',
    'lib/utils',
    'tmpl!layout'
], function(_, BaseView, BlogView, EmbedCode, Blog, Liveblog, loadTheme, utils) {

    return BaseView.extend({

        initialize: function() {
            var self = this;

            utils.dispatcher.trigger('initialize.layout-view', this);

            // Set `liveblog.render` object with what should be rendered.
            // Options:
            // * `seo`: generate the live blog HTML server side.
            // * `embed`: add embed code for making use of client side only functionality,
            // like receiving live updates.
            // * `index`: render index.html template, if the live-blog is not embedded
            // in a page (mostly for testing purposes).
            // * `livereload`: development only, reloads the page when a file is edited.
            if (_.isString(liveblog.render)) {
                var render = liveblog.render.split(',');
                liveblog.render = {};
                _.each(render, function(value) {
                    liveblog.render[value] = true;
                });
            }

            this.setTemplate('layout');

            // Create and fetch blog model and insert the blog view into the layout.
            this.model = new Liveblog(liveblog);
            this.blogModel = new Blog({Id: liveblog.id});
            this.blogModel.fetch({
                success: function() {
                    var config = self.blogModel.get('EmbedConfig');
                    if (_.has(self.blogModel.get('Language'), 'Code')) {
                        config.language = self.blogModel.get('Language').Code;
                    }
                    loadTheme(config, function() {
                        self.insertView('[data-gimme="liveblog-layout"]', new BlogView({model: self.blogModel}));
                    });
                },
                error: function() {
                    utils.dispatcher.trigger('blog-model.request-failed');
                }
            });

            self.insertView('[data-gimme="liveblog-embed-code"]', new EmbedCode({model: this.model}));
        },

        // Backbone.LayoutManager `afterRender`.
        afterRender: function() {
            utils.dispatcher.trigger('after-render.layout-view', this);
        },

        // Backbone.LayoutManager `beforeRender`.
        beforeRender: function() {
            utils.dispatcher.trigger('before-render.layout-view', this);
        },

        // Backbone.LayoutManager `serialize`.
        serialize: function() {
            return this.model.toJSON();
        }
    });
});
