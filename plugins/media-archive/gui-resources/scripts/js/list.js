define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    'gizmo/views/list',
    config.guiJs('media-archive', 'models/meta-types'),
    'tmpl!media-archive>list',
    'tmpl!media-archive>item',
],

function($, superdesk, giz, gizList, MetaTypes)
{
    var 
    Source = giz.Model.extend({url: new giz.Url('Superdesk/Source')}),
    Sources = new (giz.Collection.extend({ model: Source, href: new giz.Url('Superdesk/Source') })),
    Collaborator = giz.Model.extend
    ({
        url: new giz.Url('Superdesk/Collaborator'),
        sources: Sources
    }),
    PersonCollaborators = giz.Collection.extend({model: Collaborator});
    // ---
        
    ItemView = gizList.ItemView.extend
    ({
        model: null,
        tagName: 'div',
        init: function()
        {
            var self = this;
            this.model.on('read update', this.render, this);
            this.model.on('delete', function(){ self.el.remove(); });
        },
        tmpl: 'media-archive>item',
        render: function()
        {
            $(this.el).tmpl(this.tmpl, {Item: this.model.feed()});
            $(this.el).prop('model', this.model).prop('view', this);
            return this;
        },
        update: function(data)
        {
        },
        updateMeta: function(data)
        {
        },
        remove: function()
        {
            this.model.remove().sync();
        }
    }),
    
    ListView = gizList.ListView.extend
    ({
        users: null,
        events:
        {
        },
        item: ItemView,
        getCollection: function()
        {
            return !this.collection ? new MetaTypes : this.collection;
        }
    }),
    
    listView = new ListView(); 
    
    return function(){ listView.activate(); };
});

