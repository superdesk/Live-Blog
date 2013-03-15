define
([
    'jquery',
    'gizmo/superdesk',
    'gizmo/views/list',
    'gizmo/superdesk/action',
    config.guiJs('superdesk/user', 'models/user'),
    'tmpl!superdesk/content-article>list',
    'tmpl!superdesk/content-article>list-item',
    'tmpl!core>layouts/footer',
    'tmpl!core>layouts/footer-static',
    'tmpl!core>layouts/footer-dinamic'
],

function($, giz, gizList, Action, User)
{
    var
    MockModel = giz.Model.extend({}),
    MockCollection = giz.Collection.extend
    ({
        model: MockModel,
        href: new giz.Url('Content/Article'),
        /*
        sync: function()
        {
            var self = this,
                dfd = new $.Deferred;
            dfd.done(function(){ self._list = self._parse({AList:[{Title: 'Demo Article', Id: '1'}, {Title: 'Demo Hamster', Id: '2'}, {Title: 'Miau Hamster', Id: '3'}, {Title: 'Gorgeous Hamster', Id: '4'}]}); });
            dfd.resolve();
            return dfd;
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
                var user = new User((new giz.Url('HR/User')).get()+'/'+id)
                user.sync().done(function(){ userCache.list[user.get('Id')]; dfd.resolve(user); })
            }
            else dfd.resolve(userCachelist[id]);
            return dfd;   
        }
    },

    ItemView = gizList.ItemView.extend
    ({ 
        tmpl: 'superdesk/content-article>list-item',
        render: function()
        { 
            var self = this,
                feed = this.model.feed();
            feed.Content = JSON.parse(feed.Content);

            $(this.el).tmpl(this.tmpl, feed, function()
            {
                userCache.get(feed.Author).done(function(data)
                {
                    $('[data-article-id="'+feed.Id+'"] [data-placeholder="Author"]', self.el).text(data.get('Name')||data.get('FullName'));    
                });
                // add view to checkbox data, for use from list multi actions
                $('[type="checkbox"]', self.el).data('view', self);
            });
            return this;
        },
        events: { '[data-action="edit"]': { "click": "edit" },
        '[data-action="delete"]': { "click": "destroy" },
        '[data-action="publish"]': { "click": "publish" },
        '[data-action="unpublish"]': { "click": "unpublish" },
        '[data-action="preview"]': { "click": "preview" }
        },
        preview: function(){
            console.log('preview');
        },
        destroy: function(){
            this.model.remove().sync();
            this.el.remove();
        },
        publish: function(){
            console.log('publish');
        },
        unpublish: function(){
            console.log('unpublish');
        },
        edit: function()
        {
            Action.initApp('modules.article.edit', this.model.get('Id'));
        }
    }),
    listViewEvents = $.extend( true, gizList.ListView.prototype.events, 
    { 
        "[data-action='multi-delete']": { "click": "multiDelete" } 
    }),
    ListView = gizList.ListView.extend
    ({
        events: listViewEvents,
        tmpl: 'superdesk/content-article>list',
        itemView: ItemView,
        getCollection: function()
        { 
            if(!this.collection) this.collection = new MockCollection;
            return this.collection; 
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
        }
    }),
    listView = new ListView();
    
    return function()
    { 
        listView.activate(); 
    };
});