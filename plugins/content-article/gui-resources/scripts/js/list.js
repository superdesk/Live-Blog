define
([
    'jquery',
    'gizmo/superdesk',
    'gizmo/views/list',
    'gizmo/superdesk/action',
    'tmpl!superdesk/content-article>list',
    'tmpl!superdesk/content-article>list-item',
    'tmpl!core>layouts/footer',
    'tmpl!core>layouts/footer-static',
    'tmpl!core>layouts/footer-dinamic'
],

function($, giz, gizList, Action)
{
    var
    MockModel = giz.Model.extend({}),
    MockCollection = giz.Collection.extend
    ({
        model: MockModel,
        sync: function()
        {
            var self = this,
                dfd = new $.Deferred;
            dfd.done(function(){ self._list = self._parse({AList:[{Title: 'Demo Article', Id: '1'}]}); });
            dfd.resolve();
            return dfd;
        }
    }),
    ItemView = gizList.ItemView.extend
    ({ 
        tmpl: 'superdesk/content-article>list-item',
        render: function()
        { 
            $(this.el).tmpl(this.tmpl, this.model.feed());
            return this;
        },
        events: { '[data-action="edit"]': { "click": "edit" }},
        edit: function()
        {
            Action.initApp('modules.article.edit', this.model.get('Id'));
        }
    }),
    ListView = gizList.ListView.extend
    ({
        tmpl: 'superdesk/content-article>list',
        itemView: ItemView,
        getCollection: function()
        { 
            if(!this.collection) this.collection = new MockCollection;
            return this.collection; 
        }
    }),
    listView = new ListView();
    
    return function()
    { 
        listView.activate(); 
    
    
    };
});