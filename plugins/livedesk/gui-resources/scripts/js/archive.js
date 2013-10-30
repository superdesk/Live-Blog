define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk',
    'gizmo/superdesk/action',
    config.guiJs('livedesk', 'models/blog'),
    'tmpl!livedesk>archive/list',
    'tmpl!livedesk>archive/item',
    'tmpl!livedesk>layouts/main',
    'tmpl!core>layouts/footer',
    'tmpl!core>layouts/footer-static',
    'tmpl!core>layouts/footer-dinamic',
],
function($, superdesk, giz, Action, Blog)
{
    var 
    ItemView = giz.View.extend
    ({
        tagName: 'tr',
        events: {
            '[data-action="hide"]': { click: 'hide'}
        },
        model: null,
        init: function()
        {
            var self = this;
            this.model.on('read update', this.render, this);
            // this.model.on('delete', function(){ self.el.remove(); })
        },
        render: function()
        {
            $(this.el).tmpl('livedesk>archive/item', {User: this.model.feed()});
            $(this.el).prop('model', this.model).prop('view', this);
            $('.view', this.el).prop('model', this.model).prop('view', this);
            return this;
        },
        update: function(data)
        {
            for( var i in data ) this.model.set(i, data[i]);
            return this.model.sync();
        },
        remove: function()
        {
            this.model.remove().sync();
        },
        hide: function(evt)
        {
            evt.preventDefault();
            var self = this;

            self.model.hideSync().done(function(){
              self.el.remove();
            });
        },
        show: function()
        {
            $(this.el).removeClass('hide');
        }
    }),
    ListView = giz.View.extend
    ({
        users: null,
        events:
        {
            '[name="search"]': { 'keypress': 'key2Search' },
            '[data-action="search"]': { 'click': 'search' },
            '[data-action="cancel-search"]': { 'click': 'cancelSearch' },
            '.pagination a': { 'click': 'switchPage' }
        },
        
        key2Search: function(evt)
        {
            if(evt.keyCode == 27 ) 
            { 
                $('[data-action="cancel-search"]', this.el).trigger('click'); 
                evt.preventDefault(); 
            }
            if(evt.keyCode == 13) $('[data-action="search"]', this.el).trigger('click');
        },
        cancelSearch: function()
        {
            $('[name="search"]', this.el).val('');
            $('[data-action="search"]', this.el).trigger('click');
        },
        
        /*!
         * pagination handler
         */
        switchPage: function(evt)
        {
            if( this.syncing ) return;
            if( $(evt.target).attr('data-pagination') == 'currentpages' )
            {
                this.page.offset = $(evt.target).attr('data-offset');
                this.activate();
            }
            if( $(evt.target).attr('data-pagination') == 'prev' )
            {
                var o = parseInt(this.page.offset) - parseInt(this.page.limit);
                if( o >= 0 ) { this.page.offset = o; this.activate(); } 
            }
            if( $(evt.target).attr('data-pagination') == 'next' )
            {
                var o = parseInt(this.page.offset) + parseInt(this.page.limit);
                if( o < this.page.total ) { this.page.offset = o; this.activate(); } 
            }
        },
        /*!
         * search box handler
         */
        search: function()
        {
            var self = this,
                src = $('[name="search"]', self.el).val().toLowerCase();
            if( src.length <= 1 )
            {
                this.activate();
                $('[data-action="cancel-search"]', self.el).addClass('hide');
                return;
            }
            
            this.collection._list = []
            this.syncing = true;
            this.collection.xfilter('*').sync({data: {'title.ilike': '%'+src+'%'}, done: function(data){ self.syncing = false; }});
            
            $('[data-action="cancel-search"]', self.el).removeClass('hide');
        },
        /*!
         * a fix for gizmo.js view events bug
         */
        _resetEvents: false,
        init: function()
        {
            var self = this;
            
            this.page = { limit: 10, offset: 0, total: null, pagecount: 5 };
            
            this.collection = giz.Auth(new (giz.Collection.extend({ model: Blog, href: new giz.Url('LiveDesk/Blog') })));
            this.collection.param('Flase','isOpen');
            this.collection.asc('createdOn');
            this.collection.on('read update', this.renderList, this);
            
            this._resetEvents = false;
        },
        activate: function()
        {
            if( this._resetEvents ) this.resetEvents();
            this._resetEvents = true;
            
            var self = this;
            this.collection._list = [];
            this.syncing = true;
            this.collection.xfilter('*').sync({data: {limit: this.page.limit, offset: this.page.offset},
                done: function(data){ self.syncing = false; self.page.total = data.total; self.render(); }});
        },
        
        addItem: function(model)
        {
            $('table tbody', this.el).append( (new ItemView({ model: model })).render().el );
        },
        
        paginate: function()
        {
            this.page.currentpages = [];
            for( var i= -this.page.pagecount/2; i < this.page.pagecount/2; i++ )
            {
                var x = parseInt(this.page.offset) + (Math.round(i) * this.page.limit);
                if( x < 0 || x >= this.page.total ) continue;
                var currentpage = {offset: x, page: (x/this.page.limit)+1};
                if( Math.round(i) == 0 ) currentpage.className = 'active';
                this.page.currentpages.push(currentpage);
            }
        },
        
        renderList: function()
        {
            $('table tbody', this.el).html('');
            var self = this;
            this.collection.each(function(){ self.addItem(this); });
        },
        
        render: function()
        {
            this.paginate();
            var data = {pagination: this.page},
                self = this;
            superdesk.applyLayout('livedesk>archive/list', data, function()
            {
                // new ItemView for each models 
                self.renderList();
            });
            $.superdesk.hideLoader();
        }
        
    }),
    // TODO table partial view
    ListView1 = ListView.extend({}),
    listView = new ListView1({ el: '#area-main' }); 
    
    return function(){ listView.activate(); };
});

