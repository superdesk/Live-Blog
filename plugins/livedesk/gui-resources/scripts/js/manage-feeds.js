define([
    'jquery',
    'gizmo/superdesk',

    'tmpl!livedesk>layouts/livedesk',
    'tmpl!core>layouts/footer',
    'tmpl!core>layouts/footer-static',
	'tmpl!livedesk>manage-feeds',
	'tmpl!livedesk>manage-feeds-provider',
	'tmpl!livedesk>manage-feeds-external-blog',
    'tmpl!livedesk>manage-feeds-edit'
], function ($, Gizmo) {

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
            if ('href' in response) {
                this.url = response.href;
                this.id = parseId(this.url);
            }

            if ('Id' in response) {
                return {
                    'Id': response.Id,
                    'Name': response.Name,
                    'URI': response.URI.href
                };
            }
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
            var model = this.findSource(source);
            if (model) {
                return;
            }

            this.create({
                Name: source.get('Title'),
                URI: source.get('href'),
                Provider: source.provider
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
                this.remove(model);
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
            return this.findWhere({URI: source.get('href')});
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

        /**
         * Get external blogs collection
         *
         * @return {ExternalBlogCollection}
         */
        getBlogs: function() {
            return new ExternalBlogCollection([], {url: this.get('URI')});
        },

        validate: function(attributes) {
            if (!attributes.Name.length) {
                return 'Please set the Name';
            }

            if (!attributes.URI.length) {
                return 'Please set the URL';
            }
        }
    });

    /**
     * Global External Blog Provider Collection
     */
    var ProviderCollection = Backbone.Collection.extend({
        model: Provider,

        sortBy: function(model) {
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
            return sources.hasSource(this);
        },

        activate: function() {
            sources.addSource(this);
        },

        deactivate: function() {
            sources.removeSource(this);
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
     * List of external blogs view for single provider.
     */
    var ExternalBlogListView = Backbone.View.extend({
        initialize: function() {
            // @todo using synced.done because of not rendering anything after re-navigating
            // this.collection.on('read', this.render, this);
        },

        render: function() {
            var list = $(this.el);
            list.empty();

            var provider = this.model;
            this.collection.each(function(model) {
                model.provider = provider.id;
                var view = new ExternalBlogView({model: model});
                list.append(view.render().el);
            });

            return this;
        }
    });

    /**
     * Provider View
     */
    var ProviderView = Backbone.View.extend({
        tagName: 'li class="chain-source"',

        events: {
            'click .remove': '_remove',
            'click .edit': '_edit'
        },

        initialize: function() {
            this.model.on('change', this.render, this);
        },

        render: function() {
            var data = {Name: this.model.get('Name')};
            this.$el.tmpl('livedesk>manage-feeds-provider', data).addClass('chain-source');

            this.collection = this.model.getBlogs();
            this.collection.on('reset', this.renderCollection, this);
            this.collection.fetch({headers: {'X-Filter': 'Title, Description'}, reset: true});
            return this;
        },

        renderCollection: function() {
            this.$el.find('.chain-source-count').text(this.collection.length);
            var list = new ExternalBlogListView({collection: this.collection, model: this.model, el: this.$el.find('.chain-source-content')});
            list.render();
            return this;
        },

        _remove: function(e) {
            e.preventDefault();
            this.remove();
            this.model.destroy();
        },

        _edit: function(e) {
            e.preventDefault();
            new EditProviderView({model: this.model});
        }
    });

    /**
     * List of providers view.
     */
    var ListBlogProviderView = Backbone.View.extend({
        initialize: function() {
            this.collection.on('add', this.render, this);
            this.collection.on('reset', this.render, this);
        },

        render: function() {
            var list = $(this.el);
            list.empty();

            this.collection.each(function(model) {
                var view = new ProviderView({model: model});
                list.append(view.render().el);
            });

            if (!this.collection.length) {
                list.append($('<li />').text(_("So far there are no providers. Start with Add New Source button.")));
            }

            return this;
        }
    });

    /**
     * Edit Provider View
     */
    var EditProviderView = Backbone.View.extend({
        events: {
            'click #edit-provider-save': 'save',
            'click #edit-provider-cancel': 'close',
            'click .close': 'close'
        },

        initialize: function() {
            this.render();
        },

        render: function() {
            $(this.el).tmpl('livedesk>manage-feeds-edit');
            this.title = $(this.el).find('#edit-provider-title');
            this.url = $(this.el).find('#edit-provider-url');
            this.modal = $(this.el).find('.modal');

            if (this.model) {
                this.title.val(this.model.get('Name'));
                this.url.val(this.model.get('URI'));
                $(this.el).find('h3').text(_('Edit Provider ' + this.model.get('Name')));
            } else {
                $(this.el).find('h3').text(_('Add Provider'));
            }

            $('#area-main').append(this.el);
            this.modal.modal('show');
            return this;
        },

        save: function() {
            var data = {
                Name: this.title.val(),
                URI: this.url.val()
            };

            if (!this.model) {
                this.collection.create(data);
            } else {
                this.model.save(data);
            }

            return this.close();
        },

        close: function() {
            this.modal.modal('hide');
            this.remove();
            return false;
        }
    });

    /**
     * Main View
     */
    var MainView = Backbone.View.extend({
        el: '#area-main',

        events: {
            'click a[href="#AddSource"]': 'renderAdd'
        },

        initialize: function() {
            this.collection.on('reset', this.render, this);
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
            var list = new ListBlogProviderView({collection: this.collection, el: '#provider-list'});
            list.render();
        },

        renderAdd: function(e) {
            e.preventDefault();
            new EditProviderView({collection: this.collection});
        }
    });

    // blog sources
    var sources = new SourceCollection();

    // blog providers
    var providers = new ProviderCollection();
    providers.url = getGizmoUrl('Data/SourceType/' + PROVIDER_TYPE + '/Source');

    return function(blogHref) {
        var blog = Gizmo.Auth(new Gizmo.Register.Blog(blogHref));
        blog.sync().done(function() {
            // we need blog specific sources
            sources.url = blog.get('Source').href;

            // we need sources for rendering providers, so define rendering providers when sources are fetched
            sources.on('reset', function() {
                new MainView({model: blog, collection: providers});
                providers.fetch(fetchOptions);
            });

            // start
            sources.fetch(fetchOptions);
        });
    };
});
