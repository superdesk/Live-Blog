define
([
    'jquery',
    'jquery/superdesk',
    'gizmo/superdesk'
],

// TODO remove cleanup duplicate code

function($, superdesk, giz)
{
    /*!
     * item view
     */
    var ItemView = giz.View.extend
    ({
        tagName: 'tr',
        tmpl: '',
        model: null,
        init: function()
        {
            var self = this;
            this.model.on('read update', this.render, this);
            this.model.on('delete', function(){ self.el.remove(); });
        },
        render: $.noop,
        remove: function()
        {
            this.model.remove().sync();
        }
    }),
    /*!
     * main list
     */
    ListView = giz.View.extend
    ({
        events:
        {
            '[name="search"]': { 'keypress': 'key2Search' },
            '[data-action="search"]': { 'click': 'search' },
            '[data-action="cancel-search"]': { 'click': 'cancelSearch' },
            '.pagination a': { 'click': 'switchPage' }
        },
        
        /*!
         * search handlers
         */
        search: function()
        {
            var self = this,
                src = $('[name="search"]', self.el).val().toLowerCase();
            if( src.length <= 1 )
            {
                this.refresh();
                $('[data-action="cancel-search"]', self.el).addClass('hide');
                return;
            }
            
            this.collection._list = [];
            this.syncing = true;
            this.collection.xfilter('*').sync({data: this.searchData(src), done: function(data){ self.syncing = false; }});
            
            $('[data-action="cancel-search"]', self.el).removeClass('hide');
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
         * hook before search sync
         */
        searchData: function(src){ return {}; },
        /*!
         * pagination handler
         */
        switchPage: function(evt)
        {
            switch(true)
            {
                case this.syncing: return;
                // page number
                case $(evt.target).attr('data-pagination') == 'currentpages':
                    this.page.offset = $(evt.target).attr('data-offset');
                    this.refresh();
                    break;
                // previous page
                case $(evt.target).attr('data-pagination') == 'prev':
                    var o = parseInt(this.page.offset) - parseInt(this.page.limit);
                    if( o >= 0 ) { this.page.offset = o; this.refresh(); } 
                    break;
                // next page
                case $(evt.target).attr('data-pagination') == 'next':
                    var o = parseInt(this.page.offset) + parseInt(this.page.limit);
                    if( o < this.page.total ) { this.page.offset = o; this.refresh(); } 
                    break;
                // first page
                case $(evt.target).attr('data-pagination') == 'first':
                    this.page.offset = 0; 
                    this.refresh();
                    break;
                // last page
                case $(evt.target).attr('data-pagination') == 'last':
                    this.page.offset = this.page.total - (this.page.total % this.page.limit); 
                    this.refresh();
                    break;
                // items per page
                case $(evt.target).attr('data-ipp') > 0:
                    this.page.limit = $(evt.target).attr('data-ipp');
                    this.refresh();
                    break;
            }
        },
        /*!
         * the list collection, to be initialized later
         */
        collection: null,
        /*!
         * initialize 
         */
        init: function()
        {
            var self = this;
            this.page = // pagination data 
            { 
                limit: 25, 
                offset: 0, 
                total: null, 
                pagecount: 5, 
                ipp: [25, 50, 100], 
                isipp: function(chk, ctx){ return ctx.current() == ctx.get('limit') ? "disabled" : ""; }
            };
            this.collection = this.getCollection();
            this._resetEvents = false;
        },
        /*!
         * get collection
         * ex: giz.Auth(new (giz.Collection.extend({ model: User, href: new giz.Url('Superdesk/User') })));
         */
        getCollection: function()
        {
            return !this.collection ? new (giz.Collection.extend({ model: giz.Model})) : this.collection;
        },
        /*!
         * refresh collection data
         */
        refresh: function(opts)
        {
            var self = this;
            this.collection._list = [];
            this.syncing = true;
            var options = {data: self.refreshData(), done: function(data)
            { 
                self.syncing = false; 
                self.page.total = data.total;
            }};
            return this.collection.xfilter('*').sync(options).done(function(){ self.render(); });
        },
        /*!
         * hook before refresh sync
         * adds pagination data by default
         */
        refreshData: function()
        {
            return {limit: this.page.limit, offset: this.page.offset};
        },
        activate: function()
        {
            var self = this;
            return this.refresh().done(function()
            {
                $(superdesk.layoutPlaceholder).html(self.el);
                if( self._resetEvents ) self.resetEvents();
                self._resetEvents = true;
            });
        },
        /*!
         * compute pagination data
         */
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
        item: ItemView,
        /*!
         * add one item to the list
         */
        addItem: function(model)
        {
            $('table tbody', this.el).append( (new (this.item)({ model: model })).render().el );
        },
        /*!
         * render the complete list
         */
        renderList: function()
        {
            $('table tbody', this.el).html('');
            var self = this;
            this.collection.each(function(){ self.addItem(this); });
        },
        tagName: 'span',
        tmpl: '',
        /*!
         * main render
         * adds pagination, renders the template
         */
        render: function(cb)
        {
            this.paginate();
            var data = {pagination: this.page},
                self = this;
            $.tmpl(self.tmpl, data, function(e, o)
            {
                self.el.html(o);
                // execute after render callback
                $.isFunction(cb) && cb.apply(self);
                // render list
                self.renderList();
                // render again on read and update
                self.collection.on('read update', self.renderList, self);
            });
            $.superdesk.hideLoader();
        }
        
    });
    return { ListView: ListView, ItemView: ItemView };
});

