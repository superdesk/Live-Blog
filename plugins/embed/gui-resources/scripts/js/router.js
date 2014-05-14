'use strict';
define([
    'backbone-custom',
    'views/blog',
    'models/blog',
    'load-theme'
], function(Backbone, BlogView, Blog, loadTheme) {
    return Backbone.Router.extend({
        'routes': {
            '*path': 'default'
        },
        'default': function(path) {
            // TODO: Throw error if blog id missing
            if (liveblog.id) {
                var blog = new Blog({Id: liveblog.id});
                blog.fetch({success: function() {
                    loadTheme(blog.get('EmbedConfig'), function() {
                        var blogView,
                            blogViewSel = '[data-gimme="blog.view"]',
                            blogViewRootEl = Backbone.$(blogViewSel);
                        if (blogViewRootEl.length !== 0) {
                            blogView = new BlogView({el: blogViewSel, model: blog});
                        } else {
                            blogView = new BlogView({el: liveblog.el, model: blog});
                        }
                        blogView.conditionalRender();
                    });
                }});
            }
        }
    });
});
