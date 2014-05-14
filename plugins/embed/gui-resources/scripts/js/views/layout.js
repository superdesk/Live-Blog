/* jshint maxparams: 9 */
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
            if (_.isString(liveblog.render)) {
                var render = liveblog.render.split(',');
                liveblog.render = {};
                _.each(render, function(value) {
                    liveblog.render[value] = true;
                });
            }
            this.model = new Liveblog(liveblog);
            this.blogModel = new Blog({Id: liveblog.id});
            this.blogModel.fetch({
                success: function() {
                    var config = self.blogModel.get('EmbedConfig'),
                        lang = self.blogModel.get('Language');
                    if (lang && lang.Code) {
                        config.language = lang.Code;
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
            this.setTemplate('layout');
        },
        afterRender: function() {
            utils.dispatcher.trigger('after-render.layout-view', this);
        },
        beforeRender: function() {

            utils.dispatcher.trigger('before-render.layout-view', this);
        },
        serialize: function() {
            return this.model.toJSON();
        }
    });
});
