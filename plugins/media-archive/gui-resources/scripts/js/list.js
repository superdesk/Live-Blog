requirejs.config
({
    paths: 
    { 
        'media-types': config.gui('media-archive/scripts/js/types')
    }
});
define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    'gizmo/views/list',
    config.guiJs('media-archive', 'models/meta-data'),
    config.guiJs('media-archive', 'models/meta-type'),
    config.guiJs('media-archive', 'add'),
    'tmpl!media-archive>list',
    'tmpl!media-archive>item',
],
function($, superdesk, giz, gizList, MetaData, MetaType, Add)
{
    var 
    MetaDataCollection = giz.Collection.extend({ model: MetaData, href: new giz.Url('Archive/MetaData') }),
    MetaTypeCollection = giz.Collection.extend({ model: MetaType, href: new giz.Url('Archive/MetaType') }),
    // ---
        
    /*!
     * @see gizmo/views/list/ItemView
     */
    ItemView = gizList.ItemView.extend
    ({
        model: null,
        tagName: 'div',
        tmpl: 'media-archive>item',
        render: function()
        {
            require(['media-types/'+this.model.get('Type')+'/grid-view']);
            $(this.el).tmpl(this.tmpl, {Item: this.model.feed()});
            $(this.el).prop('model', this.model).prop('view', this);
            return this;
        },
        remove: function()
        {
            this.model.remove().sync();
        }
    }),
    
    /*!
     * @see gizmo/views/list/ListView
     */
    ListView = gizList.ListView.extend
    ({
        users: null,
        events:
        {
            '[data-action="add-media"]': { 'click' : 'add' }
        },
        itemView: ItemView,
        tmpl: 'media-archive>list',
        itemsPlaceholder: '.main-content-inner',
        init: function()
        {
            gizList.ListView.prototype.init.call(this);
            var self = this;
            $(Add).on('uploaded', function(e, Id){ self.uploaded.call(self, Id); });
        },
        /*!
         * @return MetaDataCollection
         */
        getCollection: function(){ return !this.collection ? (this.collection = new MetaDataCollection) : this.collection; },
        /*!
         * @see gizmo/views/list/ListView.refreshData
         */
        refreshData: function()
        {
            data = gizList.ListView.prototype.refreshData.call(this);
            data.thumbSize = 'medium';
            data.desc = 'createdOn';
            return data;
        },
        /*!
         * available display mode (actual file names)
         */
        displayModes: ['grid-view', 'list-view'],
        /*!
         * current display mode
         */
        displayMode: 0,
        /*!
         * return item view, applied for each item
         */
        getItemView: function(model)
        {
            console.log('get view');
            // make a placeholder element to append the new view after it has been loaded
            var placeEl = $('<span />'),
                self = this;
            superdesk.getAction('modules.media-archive.'+model.get('Type'))
            .done(function(action)
            {
                if( action && action.ScriptPath ) 
                    // TODO clean up this path
                    // TODO fallback on default
                    require([superdesk.apiUrl+action.ScriptPath+self.displayModes[self.displayMode]+'.js'],
                            function(View)
                            { 
                                try
                                { 
                                    // render new item view
                                    var newItemView = (new View({ model: model, el: placeEl }));
                                    newItemView.render();
                                    // look for recently uploaded item to popup edit
                                    if( self.recentlyUploaded && self.recentlyUploaded == model.get('Id') )
                                    {
                                        newItemView.edit();
                                        self.recentlyUploaded = null;
                                    }
                                }
                                catch(e){ console.log(View); }
                            });
            });
            
            return placeEl;
        },
        /*!
         * display add media box
         */
        add: function()
        {
            Add.activate();
        },
        /*!
         * using this to popup edit upon upload
         */
        recentlyUploaded: null,
        /*!
         * handler for upload
         */
        uploaded: function(Id)
        {
            this.recentlyUploaded = Id;
            this.page.offset = 0;
            this.refresh();
        }
        
    }),
    
    listView = new ListView(); 
    
    return function(){ listView.activate(); };
});

