define
([ 
    
    'jquery',
    'gizmo/superdesk',
    config.guiJs('livedesk', 'action'),
    'gizmo/superdesk/action',
    'jquery/superdesk',
    config.guiJs('livedesk', 'models/blogsarchive'),
    config.guiJs('livedesk', 'models/blog'),
	config.guiJs('livedesk', 'models/posttype'),
    config.guiJs('livedesk', 'models/post'),
    config.guiJs('livedesk', 'models/liveblogs'),
    'tmpl!livedesk>layouts/dashboard',
    'tmpl!livedesk>layouts/dashboard-archive',
    'tmpl!livedesk>layouts/main',
    'tmpl!core>layouts/footer',
    'tmpl!core>layouts/footer-static',
    'tmpl!core>layouts/footer-dinamic',
    'tmpl!livedesk>error-notif',
 ], 
function($, Gizmo, BlogAction, Action, superdesk, BLOGSArchive) 
{
    var 

    DashboardApp = Gizmo.View.extend
    ({
        ipp: 15,
        events: 
        { 
            '#grid_view': { 'click' : 'switchViewType' },
            '#list_view': { 'click' : 'switchViewType' },
            '#welcome-screen-create-liveblog': { 'click': 'createBlog' },
            '#search-archive-button': { 'click': 'searchArchiveHandle' },
            '#search-archive-clear': { 'click': 'searchArchiveClear' },
            '#pag-first': { 'click': 'pageFirst' },
            '#pag-prev': { 'click': 'pagePrev' },
            '#pag-next': { 'click': 'pageNext' },
            '#pag-last': { 'click': 'pageLast' },
            '.ippli': { 'click': 'itemsPerPage' }
        },
        init: function()
        {
            this.collection = Gizmo.Auth(new Gizmo.Register.LiveBlogs({href: localStorage.getItem('superdesk.login.selfHref')+'/Blog?isOpen=true'}));
            this.collection.on('read update', this.render, this);
            this.ipp = 10;
        },
        /*!
         * 
         */
        switchViewType: function(evt)
        {
            if($(evt.currentTarget).attr('id') == 'grid_view')
                $(".active-blogs", this.el).removeClass("list-active-blogs");
            else
                $(".active-blogs", this.el).addClass("list-active-blogs");
        },
        /*!
         * 
         */
        searchArchive: function(title, page, order)
        {
            var self = this;
            var data = [];
            data['archive'] = [];
            title = typeof title == 'undefined' ? '' : title;
            order = typeof order == 'undefined' ? 'createdOn' : order;
            page = typeof page == 'undefined' ? 0 : page;

            offset = page * self.ipp;
            var archive = Gizmo.Auth(new BLOGSArchive({href: localStorage.getItem('superdesk.login.selfHref')+'/Blog?isOpen=false'}));
            archive.getInfoSync(title, offset, self.ipp, order).done(function(dataArchive){
                //pagination
                var total = dataArchive.total;
                var ipp = self.ipp;
                var maxpage = 0;
                if ( total > ipp) {
                    maxpage = Math.floor(total / ipp);
                    if ( total % ipp == 0 ) {
                        maxpage --;
                    } 
                }

                var bloglist = dataArchive.BlogList;
                for ( var i = 0; i < bloglist.length; i ++ ) {
                    var blog = bloglist[i];
                    data['archive'].push(blog);
                }
                var items = {
                    ippa:'',ippb:'', ippc:''
                };
                if ( data['archive'].length > 0) {
                    items.archive = data['archive'];
                }

                if ( title != '' ) {
                    items.searchkey = title;
                }
                items.page = page + 1;

                if ( dataArchive.total > self.ipp ) {
                    items.pagination = 1;
                }

                //items per page stuff
                //corky stuff
                if ( ipp == 10 || ipp == '10') {
                    items.ippa = 'disabled';
                }
                switch (ipp) {
                    case '20':
                        items.ippb = 'disabled';
                        break;
                    case '50':
                        items.ippc = 'disabled';
                        break;
                }

                //order select
                switch (order) {
                    case 'title':
                        items.sela = 'selected="selected"';
                        break;
                    case 'createdOn':
                        items.selb = 'selected="selected"';
                        break;
                    case 'lastUpdatedOn':
                        items.selc = 'selected="selected"';
                        break;
                }                 
                $.tmpl('livedesk>layouts/dashboard-archive', items, function(e,o) 
                {
                    $('#archive_blogs', self.el).html(o);
                    self.setArchiveActions(page, maxpage, self.ipp, order);
                });
            });
        },
        /*!
         * 
         */
        setArchiveActions: function(curpage, maxpage, ipp, order) 
        {
            this.page = { curpage: curpage, maxpage: maxpage, ipp: ipp, order: order };
            var self = this;
        },
        
        /*!
         * search archive
         */
        searchArchiveHandle: function(event)
        {
            var key = $('#search-archive-text', this.el).val();
            if( key.length > 0 ) this.searchArchive(key);
        },
        
        /*!
         * clear archive search
         */
        searchArchiveClear: function(event)
        {
            this.searchArchive();   
        },

        /*!
         * navigate to first page
         */
        pageFirst: function()
        {
            var key = $('#search-archive-text', this.el).val();
            var order = $('.archive-sort', this.el).val();
            this.searchArchive(key, 0, order);
        },
        
        /*!
         * navigate to previous page
         */
        pagePrev: function()
        {
            var key = $('#search-archive-text', this.el).val();
            var order = $('.archive-sort', this.el).val();
            var prevpage = 0;
            if( this.page.curpage - 1 >= 0 ) prevpage = this.page.curpage - 1;
            this.searchArchive(key, prevpage, order);
        },
        
        /*!
         * navigate to next page
         */
        pageNext: function()
        {
            var key = $('#search-archive-text', this.el).val();
            var order = $('.archive-sort', this.el).val();
            var nextpage = maxpage;
            if( this.page.curpage + 1 < maxpage ) nextpage = this.page.curpage + 1;
            this.searchArchive(key, nextpage, order);
        },
        
        itemsPerPage: function()
        {
            this.ipp = $(event.currentTarget).attr('data-ipp');
            this.searchArchive();
        },
        
        /*!
         * navigate to last page
         */
        pageLast:  function()
        {
            var key = $('#search-archive-text').val();
            var order = $('.archive-sort').val();
            this.searchArchive(key, this.page.maxpage, order);
        },
        
        /*!
         * shwo create blog dialog
         */
        createBlog: function(event)
        {
            Action.get('modules.livedesk.add')
            .done(function(action)
            {
                superdesk.showLoader();
                action.get('Script') &&
                require([action.get('Script').href], function(AddApp){ addApp = new AddApp(); });
            })
            .fail(function()
            { 
                $.tmpl('livedesk>error-notif', {Error: _('You cannot perform this action')}, function(e, o)
                {
                    var o = $(o);
                    $('#area-main').append(o);
                    $('.close', o).on('click', function(){ $(o).remove(); });
                    setTimeout(function(){ $(o).remove(); }, 3000);
                });
            }); 
            event.preventDefault();
        },
        
        render: function()
        {
            var self = this;
            var data = [];
            data['live'] = [];
            data['archive'] = [];
            self.collection.each(function()
            {
                var model = this;
                this.get('PostPublished').sync().done(function(data)
                { 
                    self.el.find('[data-model-id="'+model.get('Id')+'"]').text(data.total) 
                });
                this.get('PostUnpublished').sync().done(function(data)
                {
                    //self.el.find('[data-model-unpublished-id="'+model.get('Id')+'"]').text(data.total) 
                });
                data['live'].push(self.cleanDescription(this.data));
            });
            
            var item = { live: data['live'] };
            if( data['live'].length == 0) delete item.live;
            self.el.html('');
            $.tmpl('livedesk>layouts/dashboard', item, function(e,o) 
            {
                self.el.html(o);
                self.resetEvents();
                self.searchArchive();
                
                // show create has right else...
                Action.get('modules.livedesk.add')
                    .done(function(){ $('#welcome-screen-create-liveblog', self.el).css('display', ''); })
                    .fail(function(){ $('#welcome-screen-create-liveblog', self.el).css('display', 'none'); });
                
            });
           
            
        },
        cleanDescription: function(data) {
            var clean = data.Description;
            data.Description = clean.replace(/(<([^>]+)>)/ig,"");
            return data;
        },
        
        activate: function(element)
        {
            this.el.appendTo(element);
            this.collection.xfilter('*,Creator.*,PostPublished').sync();
        }
        
    }),
    dashboardApp = new DashboardApp();
    
    return {
        init: function(element)
        { 
            dashboardApp.activate(element);
            return dashboardApp; 
        }
    };
});
