define
([ 
    
    'jquery',
    'gizmo/superdesk',
    'jquery/superdesk',
    config.guiJs('livedesk', 'models/blogsarchive'),
    config.guiJs('livedesk', 'models/blog'),
	config.guiJs('livedesk', 'models/posttype'),
    config.guiJs('livedesk', 'models/post'),
    config.guiJs('livedesk', 'models/liveblogs'),
    'tmpl!livedesk>layouts/dashboard',
    'tmpl!livedesk>layouts/dashboard-archive'
 ], 
function($, Gizmo, superdesk, BLOGSArchive) 
{
    var 

    DashboardApp = Gizmo.View.extend
    ({
        ipp: 15,
        init: function(){
            this.collection = new Gizmo.Register.LiveBlogs;
            this.collection.on('read update', this.render, this).
                xfilter('*,Creator.*,PostPublished').sync();
            this.ipp = 10;

        },
        searchArchive: function(title, page, order){
            
            var self = this;
            var data = [];
            data['archive'] = [];
            title = typeof title == 'undefined' ? '' : title;
            order = typeof order == 'undefined' ? 'createdOn' : order;
            page = typeof page == 'undefined' ? 0 : page;

            offset = page * self.ipp;
            var archive = new BLOGSArchive;
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
                }
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
                $.tmpl('livedesk>layouts/dashboard-archive', items, function(e,o) {
                    $('#archive_blogs').html(o);
                    self.setArchiveActions(page, maxpage, self.ipp, order);
                });
            });
        },
        setArchiveActions: function(curpage, maxpage) {
            var self = this;

            //search button
            $('#search-archive-button').off('click').on('click', function(){
                var key = $('#search-archive-text').val();
                if ( key.length > 0 ) {
                    self.searchArchive(key);
                }
            });
            //clear button
            $('#search-archive-clear').off('click').on('click', function(){
                self.searchArchive();
            });

            //pagination buttons
            $('#pag-first').off('click').on('click', function(){
                var key = $('#search-archive-text').val();
                var order = $('.archive-sort').val();
                self.searchArchive(key, 0, order);
            });
            $('#pag-prev').off('click').on('click', function(){
                var key = $('#search-archive-text').val();
                var order = $('.archive-sort').val();
                var prevpage = 0;
                if ( curpage - 1 >= 0 ) {
                    prevpage = curpage - 1;
                }
                self.searchArchive(key, prevpage, order);
            });
            $('#pag-next').off('click').on('click', function(){
                var key = $('#search-archive-text').val();
                var order = $('.archive-sort').val();
                var nextpage = maxpage;
                if ( curpage + 1 < maxpage ) {
                    nextpage = curpage + 1;
                }
                self.searchArchive(key, nextpage, order);
            });
            $('#pag-last').off('click').on('click', function(){
                var key = $('#search-archive-text').val();
                var order = $('.archive-sort').val();
                self.searchArchive(key, maxpage, order);
            });

            $('.archive-sort').off('change').on('change', function(){
                var key = $('#search-archive-text').val();
                var order = $('.archive-sort').val();
                self.searchArchive(key, 0, order);
            });

            $('.archive-blogs .archive-blog-link').off('click').on('click', function(event)
            {
             superdesk.showLoader();
             var theBlog = $(this).attr('data-blog-link'), self = this;
             superdesk.getAction('modules.livedesk.edit')
             .done(function(action)
             {
                if(!action) return;
                var callback = function()
                { 
                    require([action.Script.href], function(EditApp){ EditApp(theBlog); }); 
                };
                action.Script && superdesk.navigation.bind( $(self).attr('href'), callback, $(self).text() );
            });
             event.preventDefault();
         });

            $(self.el).off('click').on('click', '.ippli', function(el, evt){
                self.ipp = $(this).attr('data-ipp');
                self.searchArchive();
            });



        },
        render: function(){
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
            var item = {
                live: data['live']
            }

            if ( data['live'].length == 0) {
                delete item.live;
            }

            $.tmpl('livedesk>layouts/dashboard', item, function(e,o) {
                $(self.el).append(o);
                //fix blog links
                $('.list-active-blogs .active-blog-link').off('click').on('click', function(event)
                {
                    superdesk.showLoader();
                    var theBlog = $(this).attr('data-blog-link'), self = this;
                    superdesk.getAction('modules.livedesk.edit')
                    .done(function(action)
                    {
                        if(!action) return;
                        var callback = function()
                        { 
                            require([action.Script.href], function(EditApp){ EditApp(theBlog); }); 
                        };
                        action.Script && superdesk.navigation.bind( $(self).attr('href'), callback, $(self).text() );
                    });
                    event.preventDefault();
                });

                //fix create new blog button
                    $('#welcome-screen-create-liveblog').off('off').on('click', function(event)
                    {
                        superdesk.showLoader();
                        superdesk.getAction('modules.livedesk.add')
                        .done(function(action)
                        {
                            action.Script &&
                            require([action.Script.href], function(AddApp){ addApp = new AddApp(); });
                        }); 
                        event.preventDefault();
                    });

                self.searchArchive();
            });
           
            
        },
        cleanDescription: function(data) {
            var clean = data.Description;
            data.Description = clean.replace(/(<([^>]+)>)/ig,"");
            return data;
        }
    }),
    dashboardApp = new DashboardApp();

    return {
        init: function(element)
        { 
            $(element).append( dashboardApp.el );
            return dashboardApp; 
        }
    };
});
