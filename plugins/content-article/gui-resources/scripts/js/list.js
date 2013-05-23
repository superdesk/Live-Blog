define
([
    'jquery',
    'gizmo/superdesk',
    'gizmo/views/list',
    'gizmo/superdesk/action',
    config.guiJs('superdesk/article', 'models/article'),
    config.guiJs('superdesk/user', 'models/user'),
    'tmpl!superdesk/article>list',
    'tmpl!superdesk/article>list-item',
    'tmpl!core>layouts/footer',
    'tmpl!core>layouts/footer-static',
    'tmpl!core>layouts/footer-dinamic'
],

function($, giz, gizList, Action, Article, User)
{
    var
    
    router = new Backbone.Router,
    
    ArticleCollection = giz.Collection.extend
    ({
        model: Article,
        href: Article.prototype.url
        /*,
        setSearchUrl: function()
        {
            this.href = new giz.Url('Content/Article/Search');
        },
        resetSearchUrl: function()
        {
            this.href = Article.prototype.url;
        }
        */
    }),

    userCache = {
        list: {},
        get: function(id)
        {
            var dfd = new $.Deferred;
            if( !userCache.list[id] )
            {
                userCache.list[id] = dfd;
                var user = new User((new giz.Url('HR/User')).get()+'/'+id);
                user.sync().done(function(){ dfd.resolve(user); });
            }
            return userCache.list[id];   
        }
    },

    ItemView = gizList.ItemView.extend
    ({ 
        tmpl: 'superdesk/article>list-item',
        render: function()
        { 
            var self = this,
                feed = this.model.feed();
            feed.Content = JSON.parse(feed.Content);
            
            $(this.el).tmpl(this.tmpl, feed, function()
            {
                userCache.get(feed.Author.Id).done(function(data)
                {
                    $('[data-article-id="'+feed.Id+'"] [data-placeholder="Author"]', self.el).text(data.get('Name')||data.get('FullName'));    
                });
                // add view to checkbox data, for use from list multi actions
                $('[type="checkbox"]', self.el).data('view', self);
            });
             $('body').attr("class","article-list");
            return this;
        },
        init: function() {
            this.model.on('read update', this.render, this);
        },
        reRender: function() {
            this.sync();
            this.render();
        },
        events: 
        { 
            '[data-action="delete"]': { "click": "destroy" },
            '[data-action="publish"]': { "click": "publish" },
            '[data-action="unpublish"]': { "click": "unpublish" }
        },
        destroy: function()
        {
            this.model.remove().sync();
            this.el.remove();
        },
        publish: function(evt)
        {
            evt.preventDefault();
            var model_id = this.model.get('Id');
            this.model.publishSync();
        },
        unpublish: function(evt)
        {
            evt.preventDefault();
            var model_id = this.model.get('Id');
            this.model.unpublishSync();
        }
    }),
    listViewEvents = $.extend( true, {}, gizList.ListView.prototype.events, 
    { 
        "[data-action='multi-delete']": { "click": "multiDelete" },
        "[data-action='add']": { 'click': 'add' }
    }),
    ListView = gizList.ListView.extend
    ({
        events: listViewEvents,
        tmpl: 'superdesk/article>list',
        itemView: ItemView,
        getCollection: function()
        {
            if(!this.collection) this.collection = new ArticleCollection;
            return this.collection; 
        },
        searchData: function(string){ return { 'search': string }; },
        add: function()
        {
            Action.initApp('modules.article.add', this.collection);
        },

        /*!
         * delete all selected from list
        */
        multiDelete: function()
        {
            // take each item, from checkbox data, and call delete on it
            $('[type="checkbox"]', self.el).each(function()
            { 
                console.log( $(this).data('view').destroy() );
                /*
                console.log($(this).data('view'));
                $(this).data('view').delete();
                */
            });
        },
        /*!
         * edit article handler
         */
        editArticle: function(id)
        {
            this.collection.get(id).done(function(model)
            {
                document.title = _('Edit article: ')+JSON.parse(model.get('Content')).Title;
                Action.initApp('modules.article.edit', model.hash()); 
            });
        }
    }),
    listView = new ListView();

    // navigate to edit article
    router.route('article/:id', function(id){ console.log(listView); listView.editArticle(id); });
    
    return function()
    { 
        listView.activate(); 
        listView.resetEvents();
    };
});