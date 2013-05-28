define([
	'providers',
	'jquery',
    'gizmo/superdesk',
    config.guiJs('livedesk', 'action'),
    'jquery/tmpl',
    'jqueryui/draggable',
    'providers/sms/adaptor',
    config.guiJs('livedesk', 'providers-templates'),
    'tmpl!livedesk>providers/sms',
    'tmpl!livedesk>providers/sms/sms-feeds',
    'tmpl!livedesk>items/item',
    'tmpl!livedesk>items/sources/sms',
    'tmpl!livedesk>items/implementors/sources/base',
    'tmpl!livedesk>items/implementors/sources/sms',
    'tmpl!livedesk>providers/no-results',
    'tmpl!livedesk>providers/generic-error',
    'tmpl!livedesk>providers/load-more',
    'tmpl!livedesk>providers/loading'
], function( providers, $, Gizmo, BlogAction) {
$.extend(providers.sms, {
    interval: 2000,
    first: true,
    oldSmss: [],
    data: [],
    topIds: [],
    keyword:[],
	init: function(){
        var self = this;
        self.data.sms = [];
        this.adaptor.init();
        this.render();
        //trigger click event for sms feed tabs
        self.el.on('click', '.feed-info button', function(evt) {
            $('.sms-header').trigger('useractions/feedclick', this);
        });
        //handle click event on sms feed tabs
        self.el.on('useractions/feedclick','.sms-header', function(e, feed){
            self.feedTab($(feed));
        });
        //handle keyword search
        self.el.on('keyup','.sms-search-query', function( e ){
            var keycode = e.keyCode;
            var feedId = self.getActiveTab();
            var keyword = $('.sms-search-query[data-feed-id="' + feedId + '"]').val();
            if ( keycode == 13 ) {
                self.keyword[feedId] = keyword;
                self.getAllSmss({cId: -1, clearResults: true});
            }
        });
        //clear keyword search
        self.el.on('click', '.sms-clear-search', function(evt) {
            var feedId = self.getActiveTab();
            $('.sms-search-query[data-feed-id="' + feedId + '"]').val('');
            self.keywords[feedId] = '';
            self.getAllSmss({cId: -1, clearResults: true});

        });
	},
    feedTab: function(feed) {
        var self = this;
        var feedId = feed.attr('data-feed-id');
        //remove 'active' class
        $('.sms-header .feed-info [data-feed-id]').each(function(){
            $(this).removeClass('active');
        });
        $('.sms-list[data-feed-id]').each(function(){
            $(this).css('display','none');
        });
        $('.sms-load-more-holder[data-feed-id]').each(function(){
            $(this).css('display','none');
        });

        $('.smstab').each(function(){
            $(this).css('display','none');
        })
       
        $('.sms-search-query[data-feed-id="' + feedId + '"]').css('display','block');
        $('.sms-clear-search[data-feed-id="' + feedId + '"]').css('display','block');
        $('.sms-list[data-feed-id="' + feedId + '"]').css('display','block');
        $('.sms-load-more-holder[data-feed-id="' + feedId + '"]').css('display','block');
        self.getAllSmss({feedId: feedId});
    },
    render: function(){
        var self = this;
        //get all feeds and generate 'holders'
        var url = new Gizmo.Url('Data/SourceType/FrontlineSMS/Source');
        feedsUrl = url.get() + '?X-Filter=Id,Name';
        $.ajax({
            url: feedsUrl,
        }).done(function(data){
            self.el.tmpl('livedesk>providers/sms', {'items': data.SourceList}, function(){
                var feeds = data.SourceList;

                if ( feeds.length == 0 ) {
                    var message = _('No SMS feeds!');
                    $.tmpl('livedesk>providers/generic-error', {message: message}, function(e,o) {
                        $('.sms-results-holder').html(o);
                        return;
                    }); 
                }

                //prepare for 0 results
                self.topIds[0] = 0;
                self.keyword[0] = '';

                //initialize the 'top cids' arrat
                for ( var i = 0; i < feeds.length; i ++ ) {
                    self.topIds[feeds[i].Id] = 0;
                    self.keyword[feeds[i].Id] = '';
                }

                //auto select first sms feed tab
                $('.feed-info [data-feed-id]').first().trigger('click');

                //prepare the auto refresh thing
                var int = window.setInterval(function(){
                    self.refreshFeeds();
                },self.interval);

            });
        });
    },
    refreshFeeds: function() {
        var self = this;
        var feedId = self.getActiveTab();
        var cId = self.topIds[feedId];
        self.getAllSmss({cId: cId, prepend: true, feedId: feedId});
    },
    getActiveTab: function() {
        return parseInt($('.sms-header .feed-info button.active').attr('data-feed-id'));
    },
    getAllSmss: function(paramObject) {
        var self = this;
        var defFeedId = self.getActiveTab();
        var keyword = $('.sms-search-query[data-feed-id="' + defFeedId + '"]').val();
        //default search data... short name 'dsd'
        var dsd = {
            offset: 0,
            limit: 5,
            cId: -1,
            query: '',
            forceAppend: false,
            prepend: false,
            keyword: '',
            clearResults: false,
            feedId: defFeedId
        }
        //search data... short name 'sd'
        var sd = $.extend({}, dsd, paramObject);

        //check to see if the search really needs to be done
        if ( $('.sms-list[data-feed-id="' + sd.feedId + '"]').html() == '' || sd.forceAppend || sd.prepend || sd.clearResults) {
            //no search with results on this feed yet or pagination
            //just go on
        } else {
            return;
        }

        var url = new Gizmo.Url('Data/Source/' + sd.feedId + '/Post');
        var keywordSearch = '';
        if ( isNaN(sd.feedId) ) {
            sd.feedId = 0;
        }
        if ( self.keyword[sd.feedId].length > 0 ) {
            keywordSearch = '&content.ilike=' + encodeURIComponent('%' + self.keyword[sd.feedId] + '%')
        }
        myUrl = url.get() + '?X-Filter=Content,Id,CreatedOn,Creator.*&desc=createdOn&offset=' + sd.offset + '&limit=' + sd.limit + '&cId.since=' + sd.cId + keywordSearch;
        //console.log('myUrl ', myUrl );
        
        $.ajax({
            url: myUrl
        }).done(function(data){
            var total = data.total;
            var smss = data.PostList;
            //clean the results
            if ( sd.clearResults) {
                self.data.sms = [];
                $('.sms-list[data-feed-id="' + sd.feedId + '"]').html('');
                $('.sms-load-more-holder[data-feed-id="' + sd.feedId + '"]').css('display','none').html('');
            }
            //prepare the data for dragging to timeline
            posts = [];
            for ( var i = 0; i < smss.length; i++ ) {
                var item = smss[i];
                item['message'] = item.Content;
                posts.push({ Meta: item });
                self.data.sms[item.Id] = item;
                //increase the 'cId' if necessary
                if ( parseInt(self.topIds[sd.feedId]) < parseInt(item.Id) ) {
                    self.topIds[sd.feedId] = parseInt(item.Id);
                }

            }
            if ( posts.length > 0 ) {
                $.tmpl('livedesk>items/item', {
                    Post: posts,
                    Base: 'implementors/sources/sms',
                    Item: 'sources/sms'
                }, function(e, o) {
                    if ( sd.prepend ) {
                        el = $('.sms-list[data-feed-id="' + sd.feedId + '"]').prepend(o).find('.smspost');
                    } else {
                        el = $('.sms-list[data-feed-id="' + sd.feedId + '"]').append(o).find('.smspost');
                    }

                    BlogAction.get('modules.livedesk.blog-post-publish').done(function(action) {
                        el.draggable(
                        {
                            revert: 'invalid',
                            containment:'document',
                            helper: 'clone',
                            appendTo: 'body',
                            zIndex: 2700,
                            clone: true,
                            start: function(evt, ui) {
                                item = $(evt.currentTarget);
                                $(ui.helper).css('width', item.width());
                                var itemNo = $(this).attr('data-id');
                                console.log( itemNo, self.data.sms );
                                var elData = self.adaptor.universal(self.data.sms[ itemNo ]);


                                $(this).data('data', elData );

                            }
                        });
                    }).fail(function(){
                        el.removeClass('draggable').css('cursor','');
                    });
                    if ( sd.prepend ) {
                        return;
                    }
                    if ( sd.offset + sd.limit < total ) {
                        $('.sms-load-more-holder[data-feed-id="' + sd.feedId + '"]').css('display','block').tmpl('livedesk>providers/load-more', {name : 'sms-load-more-' + sd.feedId}, function(){
                            $(this).find('[name="sms-load-more-' + sd.feedId + '"]').on('click', function(){
                                var offset = sd.offset + sd.limit;
                                self.getAllSmss( $.extend({}, sd, {offset: offset, forceAppend: true, clearResults: false}) );
                            });
                        });
                    } else {
                        $('.sms-load-more-holder[data-feed-id="' + sd.feedId + '"]').css('display','none').html('');
                    }
                }); 
            } else {
                //autoupdates may return 0 results and then we don't want to show 'no results message'
                if ( ! sd.prepend ) {
                    $.tmpl('livedesk>providers/no-results', {}, function(e,o) {
                        $('.sms-list[data-feed-id="' + sd.feedId + '"]').html(o);
                    });    
                }
                
            }
        });
    }
});
return providers;
});