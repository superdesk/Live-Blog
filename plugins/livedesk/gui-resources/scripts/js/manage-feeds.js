define([
    'jquery',
    'gizmo/superdesk',
    'livedesk/views/provider-edit',

    'tmpl!livedesk>layouts/livedesk',
    'tmpl!core>layouts/footer',
    'tmpl!core>layouts/footer-static',
    'tmpl!livedesk>manage-feeds',
    'tmpl!livedesk>manage-feeds-provider',
    'tmpl!livedesk>manage-sms-feed',
    'tmpl!livedesk>manage-feeds-external-blog',
], function ($, Gizmo, EditProviderView) {

    var PROVIDER_TYPE = 'blog provider';
    var BLOG_TYPE = 'chained blog';
    var SMS_TYPE = 'smsblog';
    var mainBlogId = 0;
    var smsHackUrl = '//';

    var fetchOptions = {headers: {'X-Filter': 'Id, Name, URI'}, reset: true};
    function getLastItem( myString ) {
        var hackArray = myString.split('/');
        var lastItem = hackArray[hackArray.length - 1];
        return lastItem;
    }

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

            if ('URI' in response) {
                response.URI = response.URI.href;
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

            localStorage.removeItem('selectedChainedBlog');

            this.create({
                Name: blog.get('Title'),
                URI: blog.get('href'),
                OriginURI: blog.provider.get('URI')
            }, {headers: {'X-Filter': 'Id'}});
        },

        /**
         * Remove given source from blog sources
         *
         * @param {ExternalBlog} blog
         */
        removeBlog: function(blog) {
            var source = this.findBlog(blog);
            if (source) {
                localStorage.removeItem('selectedChainedBlog');

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
            var errors = [];
            if (!attributes.Name) {
                errors.push('Name');
            }

            if (!this.isUrl(attributes.URI)) {
                errors.push('URI');
            }

            if (errors.length) {
                throw errors;
            }
        },

        isUrl: function(url) {
            return url && url.match(/^(https?:)?\/\//);
        },

        getBlogs: function() {
            //@TODO remove the explicit X-Filter parameters and just keep them in the headers
            return new ExternalBlogCollection([], {url: this.get('URI') + '?X-Filter=Title,Description'});
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
            var checked = $(e.target).attr('checked');

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
            //$input.attr('checked', ! $input.prop('checked'));
            if ( $input.attr('checked') ) {
                $input.removeAttr('checked');
            } else {
                $input.attr('checked', 'checked');
            }
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
            this.listenTo(this.model, 'change', this.render);
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
                blog.provider = provider;
                var view = new ExternalBlogView({model: blog});
                list.append(view.render().el);
            });
        },

        delete: function(e) {
            e.preventDefault();
            if (confirm(_("Removing provider will unchain its blogs.\nAre you sure to continue?"))) {
                this.model.destroy();
                this.remove();
            }
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
            'change #sms-feed-search': 'smsSearch',
            'click .sf-searchbox > a[id!="sms-clear-search"]': 'clearSearch',
            'click #sms-clear-search': 'smsClearSearch'
        },

        initialize: function() {
            this.listenTo(this.collection, 'reset', this.render);
            this.listenTo(this.collection, 'add', this.renderList);
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

            $(this.el).tmpl('livedesk>manage-feeds', data, function(){
                jQ.trigger('managefeeds/templatedone');
            });
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

        smsSearch: function(e) {
            var q = $(e.target).val();
            var sources = $(this.el).find('li[data-type="sms-feed-li"]').each(function() {
                var show = true;
                if (q.length) {
                    var text = $(this).text();
                    var reg = new RegExp(q, 'i');
                    show = reg.test(text);
                }
                $(this).toggle(show);
            });
        },

        clearSearch: function(e) {
            e.preventDefault();
            $(this.el).find('.sf-searchbox > input').val('').change();
        },

        smsClearSearch: function(e) {
            e.preventDefault();
            $(this.el).find('#sms-feed-search').val('').change();
        }
    });

    
    //Starting sms feed stuff

    //empty jQuery object
    var jQ = $({});

    

    var optionsAllFeeds = {headers: {'X-Filter': 'Name,Id'}, reset: true};
    var optionsSmsFeeds = {headers: {'X-Filter': 'Name,Id,URI'}, reset: true};
     

    var SmsFeed = Source.extend({
        idAttribute: 'Id',
        defaults: {
            Name: 'some feed',
            URI: '//'
        }
    });
    var SmsFeedsCollection = Backbone.Collection.extend({
        model: SmsFeed,
        parse: function(response) {
            return response.SourceList;
        }
    }),
    SmsFeedView = Backbone.View.extend({
        tagName: "li",
        events: {
            'change [data-type="sms-feed"]': 'checkclick'
        },
        attributes: {
            'class': 'sf-checkbox',
            'set-bg': '1',
            'data-type': 'sms-feed-li'
        },
        checkclick: function() {
            var self = this;
            if ( this.$('input').attr('checked') ) {
                //we add
                var name = this.model.get('Name');
                var newSource = {
                    Name: this.model.get('Name'),
                    Type: SMS_TYPE,
                    IsModifiable: 'True',
                    URI: SMS_TYPE + '/' + name,
                    OriginURI: name
                };
                $.ajax({
                    url: smsHackUrl,
                    type: 'POST',
                    data: newSource
                }).done(function(data) {
                    var smsblog_id = getLastItem(data.href);
                    self.$('input').attr('data-smsblog-id', smsblog_id);
                });
                //allSourceCollection.create(newSource, { wait: true, success: this.assigned } );
            } else {
                //we remove
                var smsblogId = this.$('input').attr('data-smsblog-id');
                var remUrl = smsHackUrl + '/' + smsblogId;
                $.ajax({
                    url: remUrl,
                    type: 'DELETE'
                });
            }
        },
        assigned: function() {
            allSourceCollection.fetch(optionsAllSources);
        },
        initialize: function() {
            var self = this;
            //nothing to see here
            self.render();
        },
        render: function() {
            var self = this;
            $.tmpl('livedesk>manage-sms-feed', this.model.toJSON(), function(a,o) {
                self.$el.append(o);
            });
            return this;
        }
    }),
    SmsFeedsView = Backbone.View.extend({
        tagName: "ul",
        attributes: {
            'class': 'feeds-list'
        },
        initialize: function(){
            //this.listenTo(this.collection,'reset', this.render);
        },
        render: function(){
            var self = this;
            if ( this.collection.length == 0 ) {
                self.$el.append('<li>' + _('No SMS Feeds Available') + '</li>');
            } else {
                this.collection.each(function(SmsFeed){
                    self.addOne(SmsFeed, this);
                });    
            }
            jQ.trigger('managefeeds/allfeedsloaded');
            return self;
        },
        addOne: function(SmsFeed) {
            var self = this;
            var smsFeedViewEl = new SmsFeedView({model: SmsFeed}).el;
            self.$el.append(smsFeedViewEl);
        }
    });
    
    var counter = 0;
    var runSmsFeedsView = function() {
        var self = this;
        jQ.on('managefeeds/templatedone', function(){
            $('#sms-feed-main-list').html('');
            smsFeedsView = new SmsFeedsView({collection: smsFeedsCollection, el: $('#sms-feed-main-list')}).render();
        });
    };
    

    //to get all sources
    var SourceModel = Source.extend({
        idAttribute: 'Id',
        defaults: {
            Name: 'some feed',
            URI: '//',
            OriginURI: '//'
        } 
    });
    SourceModel.bind('remove', function(){
        //
    });

    var AllSourceCollection = Backbone.Collection.extend({
        model: SourceModel,
        parse: function(response) {
            return response.SourceList;
        },
        filterType: function(xType) {
            return this.filter(function(source) {
                return source.get('Type').Key == xType;
            });
        },
        getById: function(Id){
           return this.filter(function(val) {
              return val.get("Id") == Id;
            })
        }
    });
    var optionsAllSources = {headers: {'X-Filter': '*'}, reset: true};

    var checkSelectedFeeds = function(selected) {
        for ( var i = 0; i < selected.length; i ++ ) {
            var select = selected[i];
            var feedId = select.id;
            selectJSON = select.toJSON();
            var originURI = selectJSON.OriginURI.href;
            $('[data-type="sms-feed"][data-uri="' + originURI + '"]').attr("checked", "checked").attr("data-checked", 1).attr("data-smsblog-id", selectJSON.Id);
        }
    };

    // blog sources
    var sources = new SourceCollection();
    var providers = new ProviderCollection([], {url: getGizmoUrl('Data/SourceType/' + PROVIDER_TYPE + '/Source')});
    var view = new MainView({collection: providers, el: '#area-main'});

    return function(blogHref) {

            //small hack to get the blog id
            //@TODO get it in a smarter way
            var hackArray = blogHref.split('/');
            var blogId = hackArray[hackArray.length - 1];
            mainBlogId = blogId;
            smsHackUrl = getGizmoUrl('LiveDesk/Blog/' + mainBlogId + '/Source');

            smsFeedsCollection = new SmsFeedsCollection;
            smsFeedsCollection.url = getGizmoUrl('Data/SourceType/smsfeed/Source');
            smsFeedsCollection.fetch(optionsSmsFeeds).done(function(){
                runSmsFeedsView();
            });

            allSourceCollection = new AllSourceCollection;
            //allSourceCollection.url = getGizmoUrl('LiveDesk/Blog/' + blogId + '/Source');
            allSourceCollection.url = getGizmoUrl('Data/SourceType/smsblog/Source?blogId=' + blogId + '&X-Filter=*');
            allSourceCollection.fetch({}).done(function(response){
                jQ.on('managefeeds/allfeedsloaded', function(){
                    var smsSources = allSourceCollection.filterType(SMS_TYPE);
                    checkSelectedFeeds(smsSources);
                });
            });

            view.model = Gizmo.Auth(new Gizmo.Register.Blog(blogHref));
            view.model.sync().done(function(data) {
            // we need blog specific sources
            sources.url = data.Source.href;

            // we need sources before rendering providers, so start rendering when sources are ready
            sources.on('reset', function() {
                providers.fetch(fetchOptions);
            });

            // start
            sources.fetch(fetchOptions);
        });
    };
});
