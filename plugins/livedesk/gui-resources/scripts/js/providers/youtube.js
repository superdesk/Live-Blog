/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

define('providers/youtube', [
    'providers','utils/str', 
    'jquery',
    config.guiJs('livedesk', 'action'),
    'jquery/tmpl',
    'jquery/jsonp',
    'jqueryui/draggable',
    'providers/youtube/adaptor',
    'tmpl!livedesk>providers/youtube',
    config.guiJs('livedesk', 'providers-templates'),
    'tmpl!livedesk>items/item',
    'tmpl!livedesk>items/implementors/sources/base',
    'tmpl!livedesk>items/implementors/sources/youtube',
    'tmpl!livedesk>providers/youtube/clip-item',
    'tmpl!livedesk>providers/youtube/favorite-item',
    'tmpl!livedesk>providers/google-more',
    'tmpl!livedesk>providers/load-more',
    'tmpl!livedesk>providers/no-results',
    'tmpl!livedesk>providers/error',
    'tmpl!livedesk>providers/jsonp-error',
    'tmpl!livedesk>providers/loading'
    ], function( providers, str, $, BlogAction ) {
        $.extend(providers.youtube, {
            initialized: false,
            
            data: [],
            init: function(){
                if(!this.initialized || !this.el.children(":first").length) {
                    this.adaptor._parent = this;
                    this.adaptor.init();
                }
                this.initialized = true;
            },
            render: function() {
                var self = this;
                this.el.tmpl('livedesk>providers/youtube', {}, function(){
                    $(self.el)
                    .off('click.livedesk')
                    .on('click.livedesk', '#ytb-search-controls>li', function(evt){
                        evt.preventDefault();
                        $(this).siblings().removeClass('active') .end()
                        .addClass('active');			  
                        var myArr = $(this).attr('id').split('-');
			  
                        //hide all ggl result holders
                        self.el.find('.scroller').css('visibility', 'hidden');
                        //show only the one we need
                        $('#ytb-'+myArr[1]+'-holder').css('visibility', 'visible');
                        //show/hide the 'order by' drop down'
                        if (myArr[1] != 'src') {
                            $('#ytb-order-by').css('display','none');
                        } else {
                            $('#ytb-order-by').css('display','inline');
                        }
                        
                        self.startSearch(true);
                    })
                    .off('keyup.livedesk')
                    .on('keyup.livedesk','#youtube-search-text', function(e){
                        if(e.keyCode == 13 && $(this).val().length > 0) {
                            //enter press on youtube search text
                            //check what search it is
                            self.startSearch(true);
                        }
                    })
                    .off('change' ,'#ytb-order-by')
                    .on('change' ,'#ytb-order-by', function(){
                        self.startSearch(true);
                    })
                    ;
                });	  
            },
            startSearch: function(fresh) {
                var self = this;
                fresh = typeof fresh !== 'undefined' ? fresh : false;
                var searchVal = $('#youtube-search-text').val();
                //do youtube video search
                if ( (fresh || $('#ytb-src-results').html() == '') && searchVal != '') {
                    self.doSearch(1);
                }
            },
        
            showLoading : function(where) {
                $(where).tmpl('livedesk>providers/loading', function(){
                    });
            },
            stopLoading : function(where) {
                $(where).html('');
            },
            noResults : function(where) {
                $.tmpl('livedesk>providers/no-results', {}, function(e,o) {
                    $(where).html(o);
                });
            },
            showError : function(where) {
                $.tmpl('livedesk>providers/error', {}, function(e,o) {
                    $(where).html(o);
                });
            },
            
            trimDesc : function(desc) {
                desc = typeof desc != 'undefined' ? desc : '';
                if (desc.length > 200) {
                    return desc.substring(0, 200) + ' ...';
                } else {
                    return desc;
                }
            },
            cleanContent : function(results) {
                for(var i = 0; i < results.length; i ++) {
                    if ( results[i].video ) {
                        //results[i].video.description = this.trimDesc(results[i].video.description);
                        var upDate = new Date(results[i].video.uploaded);
                        results[i].video.uploaded = upDate.toDateString();
                        results[i].uploader = results[i].video.uploader;
                    } else {
                        //results[i].description = this.trimDesc(results[i].description);
                        var upDate = new Date(results[i].uploaded);
                        results[i].uploaded = upDate.toDateString();
                    }
                }
                return results;
            },
            doSearch: function (start) {
                var self = this, el;
                var key = $('#youtube-search-text').val();
                if(key == '') {
                    return 1;
                }
                var relevance = $('#ytb-order-by').val();
                start = typeof start !== 'undefined' ? start: 1;
                //console.log('ptBefore ', pageToken);
                if (typeof pageToken === 'undefined') {
                    pageToken = '';
                }
                
                this.showLoading('#ytb-src-more');
                if (start == 1) {
                    self.data = [];
                    $('#ytb-src-results').html('');
                }
                var fullUrl = 'https://www.googleapis.com/youtube/v3/search?q='+key+'&order='+ relevance +'&key='+ this.api_key +'&part=snippet&maxResults=20&type=video';
                fullUrl += ('&pageToken=' + pageToken);
                $.ajax({
                    url: fullUrl,
                    dataType: 'json',
                    global: false,
                    success : function(myData) {
                        self.stopLoading('#ytb-src-more');
                        //map
                        var myJson = {
                                data: myData
                            },
                            results = myJson.data.items,
                            total = myJson.data.pageInfo.totalResults,
                            pageToken = myJson.data.nextPageToken? myJson.data.nextPageToken: '';
                        if (total == 0) {
                            self.noResults('#ytb-src-results');
                        } else {
                            for( var item, posts = [], i = 0, count = myJson.data.items.length; i < count; i++ ){
                                item = myJson.data.items[i];                                //create a 'mapper' to use the old templates data structure
                                item.title = item.snippet.title;
                                item.description = item.snippet.description;
                                item.thumbnail = {
                                    sqDefault: item.snippet.thumbnails.default.url
                                }
                                item.id = item.id.videoId;
                                item.updated = item.snippet.publishedAt;
                                item.uploader = item.snippet.channelTitle;
                                item.newapi = true;
                                //end mapper

                                item.type = 'search';
                                item.description_trimed = self.trimDesc(item.description);
                                item.time_formated = item.updated;
                                posts.push({ Meta: item });
                                self.data[item.id] = item;
                                //console.log('new item ', item);
                            }
                            $.tmpl('livedesk>items/item', { 
                                    Post: posts,
                                    Base: 'implementors/sources/youtube',
                                    Item: 'sources/youtube'
                                }, function(e,o) {
                                    el = $('#ytb-src-results').append(o).find('.youtube'); 
                                    BlogAction.get('modules.livedesk.blog-post-publish').done(function(action) {
                                        // var itemWidth = el.width(),
                                        //     itemHeight = el.height();
                                        // itemWidth = itemWidth > 500? 500 : itemWidth;
                                        // var containment = [
                                        //     75, 
                                        //     200, 
                                        //     $(window).width()-itemWidth-30, 
                                        //     $(window).height() - itemHeight-30
                                        // ];
                                        el.draggable({
                                            addClasses: false,
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
                                                $(this).data('data', self.adaptor.universal(self.data[ itemNo ]));
                                            }
                                        });
                                    }).fail(function(){
                                        el.removeClass('draggable');
                                    });
                                });
                        }
                        
                        
                        if (pageToken.length > 0) {
                            $('#ytb-src-more').tmpl('livedesk>providers/load-more', {
                                name : 'ytb-src-load-more'
                            }, function(){
                                $(this).find('[name="ytb-src-load-more"]').on('click', function(){
                                    self.doSearch(2);
                                });
                            });       
                        } 
                    },
                    error : function(data){
                        self.showError('#ytb-src-results');
                    }
                }).fail(function() {
                    self.stopLoading('#ytb-src-more');
                    self.showError('#ytb-src-results');
                })
            }		
        });
        return providers;
    });