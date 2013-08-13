define([
	'providers',
	'jquery',
    'gizmo/superdesk',
    config.guiJs('livedesk', 'action'),
    'jquery/tmpl',
    'jqueryui/draggable',
    'providers/comments/adaptor',
    config.guiJs('livedesk', 'providers-templates'),
    'tmpl!livedesk>providers/comments',
    'tmpl!livedesk>items/item',
    'tmpl!livedesk>items/sources/comments',
    'tmpl!livedesk>items/implementors/sources/base',
    'tmpl!livedesk>items/implementors/sources/comments',
    'tmpl!livedesk>providers/no-results',
    'tmpl!livedesk>providers/generic-error',
    'tmpl!livedesk>providers/load-more',
    'tmpl!livedesk>providers/loading'
], function( providers, $, Gizmo, BlogAction) {
$.extend(providers.comments, {
    blogId: 0,
    data: [],
    topIds: 0,
    interval: 2000,
    keyword: '',
	init: function(blogUrl){
        var self = this;
        this.adaptor.init();
        self.data.comments = [];
        $.ajax({
            url: typeof blogUrl === 'string' ? blogUrl : blogUrl[0]
        }).done(function(data){
            self.blogId = data.Id;
            self.render();
        });
    },
    render: function(){
        var self = this;
        self.el.tmpl('livedesk>providers/comments', {}, function(){
            //handle keyword search
            self.el.on('keyup','.comments-search-query', function( e ){
                var keycode = e.keyCode;
                var keyword = $('.comments-search-query').val();
                if ( keycode == 13 ) {
                    self.keyword = keyword;
                    self.getComments({cId: -1, clearResults: true});
                }
            });
            var int = window.setInterval(function(){
                self.refreshComments();
            },self.interval);
            self.getComments({});
        });
        //dynamically get size of header and set top space for list
        var top_space = $('#comments .sms-header').outerHeight() + 20;
        $('.comments-results-holder').css({'top': top_space});     
    },
    refreshComments: function() {
        var self = this;
        var cId = self.topIds;
        self.getComments({cId: cId, prepend: true});
    },
    getComments: function(paramObject) {
        var self = this;
        var dsd = {
            offset: 0,
            limit: 5,
            cId: -1,
            query: '',
            forceAppend: false,
            prepend: false,
            keyword: '',
            clearResults: false
        }
        var sd = $.extend({}, dsd, paramObject);
        //check to see if the search really needs to be done
        if ( sd.forceAppend || sd.prepend || sd.clearResults ) {
            //no search with results on this feed yet or pagination
            //just go on
        } else {
            //console.log('return ');
            //return;
        }

        var url = new Gizmo.Url('LiveDesk/Blog/' + self.blogId + '/Post/Comment/');
        var keywordSearch = '';
        if ( self.keyword.length > 0 ) {
            keywordSearch = '&content.ilike=' + encodeURIComponent('%' + self.keyword + '%')
        }
        myUrl = url.get() + '?X-Filter=AuthorName,Content,CreatedOn,CId,Id&desc=createdOn&offset=' + sd.offset + '&limit=' + sd.limit + '&cId.since=' + sd.cId + keywordSearch;
        $.ajax({
            url: myUrl
        }).done(function(data){
            var total = data.total;
            var comments = data.PostList;
            //clean the results
            if ( sd.clearResults) {
                self.data.comments = [];
                $('.comments-list').html('');
                $('.comments-load-more-holder').css('display','none').html('');
            }
            //prepare the data for dragging to timeline
            posts = [];
            for ( var i = 0; i < comments.length; i++ ) {
                var item = comments[i];
                item['message'] = item.Content;
                posts.push({ Meta: item });
                self.data.comments[item.Id] = item;
                //increase the 'cId' if necessary
                if ( parseInt(self.topIds) < parseInt(item.CId) ) {
                    self.topIds = parseInt(item.CId);
                }

            }
            if ( posts.length > 0 ) {
                $.tmpl('livedesk>items/item', {
                    Post: posts,
                    Base: 'implementors/sources/comments',
                    Item: 'sources/comments'
                }, function(e, o) {
                    if ( sd.prepend ) {
                        el = $('.comments-list').prepend(o).find('.commentpost');
                    } else {
                        el = $('.comments-list').append(o).find('.commentpost');
                    }

                    BlogAction.get('modules.livedesk.blog-post-publish').done(function(action) {
                        el.draggable(
                        {
                            revert: 'invalid',
                            //containment:'document',
                            helper: 'clone',
                            appendTo: 'body',
                            zIndex: 2700,
                            clone: true,
                            start: function(evt, ui) {
                                item = $(evt.currentTarget);
                                $(ui.helper).css('width', item.width());
                                var itemNo = $(this).attr('data-id');
                                var elData = self.adaptor.universal(self.data.comments[ itemNo ]);
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
                        $('.comments-load-more-holder').css('display','block').tmpl('livedesk>providers/load-more', {name : 'comments-load-more'}, function(){
                            $(this).find('[name="comments-load-more"]').on('click', function(){
                                var offset = sd.offset + sd.limit;
                                self.getComments( $.extend({}, sd, {offset: offset, forceAppend: true, clearResults: false}) );
                            });
                        });
                    } else {
                        $('.comments-load-more-holder').css('display','none').html('');
                    }
                }); 
            } else {
                //autoupdates may return 0 results and then we don't want to show 'no results message'
                if ( ! sd.prepend ) {
                    $.tmpl('livedesk>providers/no-results', {}, function(e,o) {
                        $('.comments-list').html(o);
                    });    
                }
                
            }
        });
    }
});
return providers;
});
