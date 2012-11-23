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
    'tmpl!media-archive>list',
    'tmpl!media-archive>item',
],
function($, superdesk, giz, gizList, MetaData, MetaType)
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
            require(['media-types/'+this.model.get('Type')+'/grid-view'], function(){ console.log(this, arguments); })
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
        },
        itemView: ItemView,
        tmpl: 'media-archive>list',
        itemsPlaceholder: '.main-content-inner',
        /*!
         * @return MetaDataCollection
         */
        getCollection: function(){ return !this.collection ? (this.collection = new MetaDataCollection) : this.collection; },
        refreshData: function()
        {
            data = gizList.ListView.prototype.refreshData.call(this);
            data.thumbSize = 'medium';
            return data;
        },
        displayModes: ['grid-view', 'list-view'],
        displayMode: 0,
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
                    require([superdesk.apiUrl+action.ScriptPath+self.displayModes[self.displayMode]+'.js'],
                            function(View)
                            { 
                                try{ (new View({ model: model, el: placeEl })).render(); }
                                catch(e){ console.log(View); }
                            });
            });
            
            return placeEl;
        }
    }),
    
    listView = new ListView(); 
    
    return function(){ listView.activate(); };
});

