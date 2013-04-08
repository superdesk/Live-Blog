define([
    'jquery',
    'gizmo/superdesk',

    'tmpl!livedesk>layouts/livedesk',
    'tmpl!core>layouts/footer',
    'tmpl!core>layouts/footer-static',
	'tmpl!livedesk>manage-feeds',
	'tmpl!livedesk>manage-feeds-provider',
	'tmpl!livedesk>manage-feeds-external-blog'
], function ($, Gizmo) {

    var BlogSource = Gizmo.Model.extend({});

    var BlogSourceCollection = Gizmo.Collection.extend({
        model: BlogSource,

        /**
         * Test if source is active for blog
         *
         * @param {ExternalBlog} source
         * @return {boolean}
         */
        hasSource: function(source) {
            return this.findSource(source) !== undefined;
        },

        /**
         * Add given source to blog sources
         *
         * @param {ExternalBlog} source
         */
        addSource: function(source) {
            this.insert({
                Name: source.get('Title'),
                URI: source.href,
                Type: 'chained blog',
                IsModifiable: false
            });
        },

        /**
         * Remove given source from blog sources
         *
         * @param {ExternalBlog} source
         */
        removeSource: function(source) {
            var model = this.findSource(source);
            if (model) {
                model.destroy();
            }
        },

        /**
         * Find model for given source
         *
         * @param {ExternalBlog} source
         * @return {BlogSource}
         */
        findSource: function(source) {
            var list = this.getList();
            for (var i in list) {
                if (list[i].get('URI').href === source.href) {
                    return list[i];
                }
            }
        }
    });

    var blogSources = null; // set later for scope

    /**
     * External Blog
     */
    var ExternalBlog = Gizmo.Model.extend({
        active: null,

        isActive: function() {
            return blogSources.hasSource(this);
        },

        activate: function() {
            if (this.isActive()) {
                return;
            }

            blogSources.addSource(this);
        },

        deactivate: function() {
            if (!this.isActive()) {
                return;
            }

            blogSources.removeSource(this);
        }
    });

    /**
     * External Blog Collection holds blogs from single provider
     */
    var ExternalBlogCollection = Gizmo.Collection.extend({
        model: ExternalBlog
    });

    /**
     * External Blog Provider
     */
    var BlogProvider = Gizmo.Model.extend({
        blogs: null,

        /**
         * Get url for both object with href or just string
         *
         * @return {string}
         */
        getUrl: function() {
            var url = this.get('URL');
            if (typeof url === 'object') {
                url = url.href;
            }

            return url;
        },

        /**
         * Get external blogs collection
         *
         * @return {ExternalBlogCollection}
         */
        getBlogs: function() {
            return new ExternalBlogCollection({href: this.getUrl()});
        }
    });

    /**
     * Global External Blog Provider Collection
     */
    var BlogProviderCollection = Gizmo.Collection.extend({
        model: BlogProvider,

        url: new Gizmo.Url('LiveDesk/BlogProvider'),

        init: function() {
            var collection = this;
            this.model.on('insert', function(model) {
                collection.trigger('add');
            });
        },

        // @todo this doesn't work
        sortBy: function(model) {
            console.log('sort', model);
            return -1 * model.get('Id');
        }
    });

    /**
     * Single External Blog View - a list item.
     */
    var ExternalBlogView = Gizmo.View.extend({
        tagName: 'li',
        
        events: {
            'input:checkbox': {change: 'change'},
            '.sf-checkbox-custom': {click: 'toggleCheckbox'}
        },

        render: function() {
            var data = this.model.feed();
            data.cid = this.model._clientId;
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
        toggleCheckbox: function(e) {
            $input = $(this.el).find('input:checkbox');
            $input.prop('checked', ! $input.prop('checked'));
            $input.change();
        }
    });

    /**
     * List of external blogs view for single provider.
     */
    var ExternalBlogListView = Gizmo.View.extend({
        init: function() {
            // @todo using synced.done because of not rendering anything after re-navigating
            // this.collection.on('read', this.render, this);
        },

        render: function() {
            var list = $(this.el);
            list.empty();

            this.collection.each(function() {
                var view = new ExternalBlogView({model: this});
                list.append(view.render().el);
            });

            return this;
        }
    });

    /**
     * Single provider view.
     */
    var BlogProviderView = Gizmo.View.extend({
        tagName: 'li class="chain-source"',

        events: {
            '.remove': {click: '_remove'},
            '.edit': {click: '_edit'}
        },

        init: function() {
            this.model.on('delete', this.remove, this);
            this.model.on('update', this.render, this);
        },

        render: function() {
            var blogs = this.model.getBlogs();
            var provider = this.model;
            var $el = $(this.el);
            var view = this;

            blogs.xfilter('Title', 'Description').sync().
                done(function() {
                    var data = provider.feed();
                    data.BlogCount = blogs.count();

                    $el.tmpl('livedesk>manage-feeds-provider', data).addClass('chain-source');
                    var list = new ExternalBlogListView({collection: blogs, el: $el.find('.chain-source-content')});
                    list.render();
                }).
                fail(function(e) {
                    var data = provider.feed();
                    data.Title = "Sorry, but can't reach '" + data.Title + "'.";
                    $el.tmpl('livedesk>manage-feeds-provider', data).addClass('chain-source');
                    $el.find('h5').css('color', '#cc0000');
                });
            return this;
        },

        _remove: function(e) {
            e.preventDefault();
            this.model.remove().sync();
        },

        _edit: function(e) {
            e.preventDefault();
            new EditBlogProviderView({model: this.model});
        }
    });

    /**
     * List of providers view.
     */
    var ListBlogProviderView = Gizmo.View.extend({
        init: function() {
            this.collection.on('read', this.render, this);
            this.collection.on('add', this.render, this);
        },

        render: function() {
            var list = $(this.el);

            list.empty();
            this.collection.each(function() {
                var modelView = new BlogProviderView({model: this});
                list.append(modelView.render().el);
            });

            if (!this.collection.count()) {
                list.append($('<li />').text(_("So far there are no providers. Start with Add New Source button.")));
            }

            return this;
        }
    });

    /**
     * Edit provider popup view.
     */
    var EditBlogProviderView = Gizmo.View.extend({
        el: '#AddSource',

        init: function() {
            this.title = $(this.el).find('#edit-provider-title');
            this.url = $(this.el).find('#edit-provider-url');

            // render on init
            this.render();
        },

        render: function() {
            if (this.model) {
                this.title.val(this.model.get('Title'));
                this.url.val(this.model.getUrl());
                $(this.el).find('h3').text(_('Edit Provider ' + this.model.get('Title')));
            } else {
                $(this.el).find('h3').text(_('Add Provider'));
            }

            $(this.el).modal('show');
        },

        events: {
            '#edit-provider-save': {click: 'save'},
            '#edit-provider-cancel': {click: 'cancel'},
            '.close': {click: 'cancel'}
        },

        save: function(e) {
            e.preventDefault();

            var data = {
                Title: this.title.val(),
                URL: this.url.val()
            };

            if (this.model) {
                this.model.set(data).sync();
            } else {
                this.collection.insert(data);
            }

            this.close();
        },

        cancel: function(e) {
            e.preventDefault();
            this.close();
        },

        close: function() {
            $(this.el).find('input:text').val('');
            $(this.el).modal('hide');
        }
    });

    /**
     * Main view.
     */
    var ManageFeedsView = Gizmo.View.extend({
        el: '#area-main',

        events: {
            'a[href="#AddSource"]': {click: 'renderAdd'}
        },

        init: function() {
            this.collection = new BlogProviderCollection();
        },

        render: function() {
            var data = this.model.feed();
            data.ui = {
                content: 'is-content=1',
                side: 'is-side=1',
                submenu: 'is-submenu',
                submenuActive4: 'active'
            };

            $(this.el).tmpl('livedesk>manage-feeds', data);
            this.renderList();
            return this;
        },

        renderList: function() {
            var list = new ListBlogProviderView({collection: this.collection, el: '#provider-list'});
            this.collection.xfilter('Id', 'Title', 'URL').sync();
        },

        renderAdd: function(e) {
            e.preventDefault();
            new EditBlogProviderView({collection: this.collection});
        }
    });

    return function(blogHref) {
        var blog = Gizmo.Auth(new Gizmo.Register.Blog(blogHref));
        blog.sync().done(function() {
            blogSources = new BlogSourceCollection({href: blog.get('Source').href});
            blogSources.xfilter('URI').sync().done(function(data) {
                var view = new ManageFeedsView({model: blog});
                view.render();
            });
        });
    };
});
