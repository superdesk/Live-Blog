define([
    'jquery',
    'gizmo/superdesk',
    'livedesk/views/provider-edit',

    'tmpl!livedesk>layouts/livedesk',
    'tmpl!core>layouts/footer',
    'tmpl!core>layouts/footer-static',
    'tmpl!livedesk>manage-feeds',
    'tmpl!livedesk>manage-feeds-provider',
    'tmpl!livedesk>manage-feeds-external-blog',
], function ($, Gizmo, EditProviderView) {

    var PROVIDER_TYPE = 'blog provider';
    var BLOG_TYPE = 'chained blog';

    var fetchOptions = {headers: {'X-Filter': 'Id, Name, URI'}, reset: true};

    /**
     * Get gizmo url for given path
     *
     * @param {string} path
     * @return {string}
     */
    function getGizmoUrl(path)
    {
        var url = new Gizmo.Url(path);
        return url.get();
    }

    /**
     * Get id from given url
     *
     * @param {string} url
     * @return {string}
     */
    function parseId(url)
    {
        return url.split('/').slice(-1)[0];
    }

    /**
     * Source Model
     */
    var Source = Backbone.Model.extend({
        idAttribute: 'Id',

        defaults: {
            Type: BLOG_TYPE,
            IsModifiable: 'True'
        },

        parse: function(response) {
            if (response === null) {
                return;
            }

            if ('href' in response) {
                this.url = response.href;
                delete response.href
            }

            return response;
        }
    });

    /**
     * Stored sources
     */
    var SourceCollection = Backbone.Collection.extend({
        model: Source,

        /**
         * Test if source is active for blog
         *
         * @param {ExternalBlog} blog
         * @return {boolean}
         */
        hasBlog: function(blog) {
            return this.findBlog(blog) !== undefined;
        },

        /**
         * Add given source to blog sources
         *
         * @param {ExternalBlog} blog
         */
        addBlog: function(blog) {
            var source = this.findBlog(blog);
            if (source) {
                return;
            }

            this.create({
                Name: blog.get('Title'),
                URI: blog.get('href'),
                Provider: blog.provider
            });
        },

        /**
         * Remove given source from blog sources
         *
         * @param {ExternalBlog} blog
         */
        removeBlog: function(blog) {
            var source = this.findBlog(blog);
            if (source) {
                this.remove(source);
                source.destroy();
            }
        },

        /**
         * Find model for given source
         *
         * @param {ExternalBlog} blog
         * @return {BlogSource}
         */
        findBlog: function(blog) {
            return this.findWhere({URI: blog.get('href')});
        },

        parse: function(response) {
            return response.SourceList;
        }
    });

    /**
     * Provider Model
     */
    var Provider = Source.extend({
        urlRoot: getGizmoUrl('Data/Source'),

        defaults: {
            Type: PROVIDER_TYPE,
            IsModifiable: 'True'
        },

        validate: function(attributes) {
            if (!attributes.Name) {
                return _('Please set the Name');
            }

            if (!attributes.URI) {
                return _('Please set the URL');
            }
        },

        getBlogs: function() {
            return new ExternalBlogCollection([], {url: this.get('URI')});
        },

        parse: function(response) {
            if (response === null) {
                return;
            }

            if ('URI' in response) {
                response.URI = response.URI.href;
            }

            return response;
        },

        render: function() {
            return {
                id: this.id,
                name: this.get('Name'),
                uri: this.get('URI')
            };
        }
    });

    /**
     * Global External Blog Provider Collection
     */
    var ProviderCollection = Backbone.Collection.extend({
        model: Provider,

        xfilter: {'X-Filter': 'Id, Name, URI'},

        comparator: function(model) {
            return -1 * model.get('Id');
        },

        parse: function(response) {
            return response.SourceList;
        }
    });

    /**
     * External Blog
     */
    var ExternalBlog = Backbone.Model.extend({
        isActive: function() {
            return sources.hasBlog(this);
        },

        activate: function() {
            sources.addBlog(this);
        },

        deactivate: function() {
            sources.removeBlog(this);
        }
    });

    /**
     * External Blog Collection holds blogs from single provider
     */
    var ExternalBlogCollection = Backbone.Collection.extend({
        model: ExternalBlog,

        parse: function(response) {
            return response.BlogList;
        }
    });

    /**
     * Single External Blog View - a list item.
     */
    var ExternalBlogView = Backbone.View.extend({
        tagName: 'li',
        
        events: {
            'change input:checkbox': 'change',
            'click .sf-checkbox-custom': 'toggleCheckbox'
        },

        render: function() {
            var data = this.model.clone().attributes;
            data.cid = this.model.cid;
            $(this.el).
                tmpl('livedesk>manage-feeds-external-blog', data).
                addClass('chain-blog');

            $(this.el).find('.sf-checkbox').each(function(i, val) {
                $(val).after('<span class="sf-checkbox-custom" target-checkbox="' + $(val).attr('name') +'"></span>');
                $(val).hide();
            });

            var $box = $(this.el).find('input:checkbox');
            $box.prop('checked', this.model.isActive());
            $box.change();

            return this;
        },

        change: function(e) {
            var checked = $(e.target).prop('checked');

            if (checked) {
                this.model.activate();
            } else {
                this.model.deactivate();
            }

            this.renderCheckbox(checked);
        },

        renderCheckbox: function(checked) {
            var $li = $(this.el);
            var $box = $(this.el).find('.sf-checkbox-custom');

            if (checked) {
                $li.addClass('active-bg');
                $box.addClass('sf-checked');
            } else {
                $li.removeClass('active-bg');
                $box.removeClass('sf-checked');
            }
        },

        /**
         * Change value and trigger change event
         */
        toggleCheckbox: function() {
            $input = $(this.el).find('input:checkbox');
            $input.prop('checked', ! $input.prop('checked'));
            $input.change();
        }
    });

    /**
     * Provider View
     */
    var ProviderView = Backbone.View.extend({
        tagName: 'li',

        events: {
            'click .remove': 'delete',
            'click .edit': 'edit'
        },

        initialize: function() {
            this.model.on('change', this.render, this);
        },

        render: function() {
            this.renderProvider();
            this.fetchBlogs();
            return this;
        },

        renderProvider: function() {
            var data = {Name: this.model.get('Name')};
            this.$el.tmpl('livedesk>manage-feeds-provider', data).addClass('chain-source');
        },

        fetchBlogs: function() {
            this.collection = this.model.getBlogs();
            this.collection.on('reset', this.renderBlogs, this);
            this.collection.fetch({headers: {'X-Filter': 'Title, Description'}, reset: true});
        },

        renderBlogs: function() {
            this.$el.find('.chain-source-count').text(this.collection.length);
            var list = $(this.el).find('.chain-source-content').empty();
            var provider = this.model;

            this.collection.each(function(blog) {
                blog.provider = provider.id;
                var view = new ExternalBlogView({model: blog});
                list.append(view.render().el);
            });
        },

        delete: function(e) {
            e.preventDefault();
            this.remove();
            this.model.destroy();
        },

        edit: function(e) {
            e.preventDefault();
            var view = new EditProviderView({model: this.model});
            this.$el.closest('#area-main').append(view.render().el);
        }
    });

    /**
     * Main View
     */
    var MainView = Backbone.View.extend({
        events: {
            'click a[href="#AddSource"]': 'renderAdd',
            'change .sf-searchbox > input': 'search',
            'click .sf-searchbox > a': 'clearSearch'
        },

        initialize: function() {
            this.collection.on('reset', this.render, this);
            this.collection.on('add', this.renderList, this);
        },

        render: function() {
            this.renderMain();
            this.renderList();
            return this;
        },

        renderMain: function() {
            var data = this.model.feed();
            data.ui = {
                content: 'is-content=1',
                side: 'is-side=1',
                submenu: 'is-submenu',
                submenuActive4: 'active'
            };

            $(this.el).tmpl('livedesk>manage-feeds', data);
        },

        renderList: function() {
            var list = $(this.el).find('#provider-list').empty();

            this.collection.each(function(provider) {
                var view = new ProviderView({model: provider});
                list.append(view.render().el);
            });

            if (!this.collection.length) {
                list.append($('<li />').text(_("So far there are no providers. Start with Add New Provider button.")));
            }

            return this;
        },

        renderAdd: function(e) {
            e.preventDefault();
            var view = new EditProviderView({collection: this.collection});
            this.$el.append(view.render().el);
        },

        search: function(e) {
            var q = $(e.target).val();
            var sources = $(this.el).find('.chain-blog').each(function() {
                var show = true;
                if (q.length) {
                    var text = $(this).text();
                    var reg = new RegExp(q, 'i');
                    show = reg.test(text);
                }

                if (show) {
                    $(this).show();
                } else {
                    $(this).hide();
                }
            });
        },

        clearSearch: function(e) {
            e.preventDefault();
            $(this.el).find('.sf-searchbox > input').val('').change();
        }
    });

    // blog sources
    var sources = new SourceCollection();

    return function(blogHref) {
        var blog = Gizmo.Auth(new Gizmo.Register.Blog(blogHref));
        blog.sync().done(function() {
            // we need blog specific sources
            sources.url = blog.get('Source').href;

            // we need sources before rendering providers, so start rendering when sources are ready
            sources.on('reset', function() {
                var providers = new ProviderCollection();
                providers.url = getGizmoUrl('Data/SourceType/' + PROVIDER_TYPE + '/Source');

                new MainView({model: blog, collection: providers, el: '#area-main'});
                providers.fetch(fetchOptions);
            });

            // start
            sources.fetch(fetchOptions);
        });
    };
});
