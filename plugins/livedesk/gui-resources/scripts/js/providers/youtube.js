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
    'tmpl!livedesk>providers/youtube/clip-item',
    'tmpl!livedesk>providers/youtube/favorite-item',
    'tmpl!livedesk>providers/google-more',
    'tmpl!livedesk>providers/load-more',
    'tmpl!livedesk>providers/no-results',
    'tmpl!livedesk>providers/jsonp-error',
    'tmpl!livedesk>providers/loading'
    ], function( providers, str, $, BlogAction ) {
        $.extend(providers.youtube, {
            initialized: false,
            
            data: [],
            init: function(){
                if(!this.initialized || !this.el.children(":first").length) {
                    this.adaptor.init();
                    this.render();
                }
                this.initialized = true;
            },
            render: function() {
                var self = this;
                this.el.tmpl('livedesk>providers/youtube', {}, function(){
                    $(self.el)
                    .off('click.livedesk')
                    .on('click.livedesk', '#ytb-search-controls>li', function(ev){
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
                if ( $('#ytb-src-tab').hasClass('active') ) {
                    //do youtube search
                    if ( (fresh || $('#ytb-src-results').html() == '') && searchVal != '') {
                        self.doSearch(1);
                    }
                }
           
                if ( $('#ytb-fav-tab').hasClass('active') ) {
                    //do youtube search
                    if (fresh || $('#ytb-fav-results').html() == '') {
                        self.doFavorites();
                    }
                }
           
                if ( $('#ytb-usr-tab').hasClass('active') ) {
                    //do youtube search
                    if (fresh || $('#ytb-usr-results').html() == '') {
                        self.doUsers();
                    }
               
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
                        results[i].video.description = this.trimDesc(results[i].video.description);
                        var upDate = new Date(results[i].video.uploaded);
                        results[i].video.uploaded = upDate.toDateString();
                        results[i].uploader = results[i].video.uploader;
                    } else {
                        results[i].description = this.trimDesc(results[i].description);
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
                start = typeof start !== 'undefined' ? start : 1;
                
                this.showLoading('#ytb-src-more');
                if (start == 1) {
                    self.data = [];
                    $('#ytb-src-results').html('');
                }
                var fullUrl = 'http://gdata.youtube.com/feeds/api/videos?v=2&max-results=20&alt=jsonc&orderby='+ relevance +'&q='+key+'&start-index='+start;
                $.ajax({
                    url : fullUrl,
                    dataType: 'json',
                    success : function(myData){
                        self.stopLoading('#ytb-src-more');
                        var myJson = myData;
                        var results = myJson.data.items;
                        var total = myJson.data.totalItems;
                        var ipp = myJson.data.itemsPerPage;
                        var start = myJson.data.startIndex;
                        
                        if( start == 1 && total == 0) {
                            self.noResults('#ytb-src-results');
                        } else {
                            $.tmpl('livedesk>providers/youtube/clip-item', {results : self.cleanContent(results)}, function(e,o) {
                                el = $('#ytb-src-results').append(o).find('.youtube')
                                BlogAction.get('modules.livedesk.blog-post-publish').done(function(action) {
                                    el.draggable({
                                        revert: 'invalid',
                                        helper: 'clone',
                                        appendTo: 'body',
                                        zIndex: 2700,
                                        clone: true,
                                        start: function(evt, ui) {
                                            item = $(evt.currentTarget);
                                            $(ui.helper).css('width', item.width());
                                            var idx = parseInt($(this).attr('idx'),10);
                                            $(this).data('data', self.adaptor.universal( results[idx] ));
                                        }   
                                    });
                                }).fail(function(){
                                    el.removeClass('draggable');
                                });
                            });
                        }
                        
                        
                        if (parseInt(start + ipp) < total) {
                            $('#ytb-src-more').tmpl('livedesk>providers/load-more', {
                                name : 'ytb-src-load-more'
                            }, function(){
                                $(this).find('[name="ytb-src-load-more"]').on('click', function(){
                                    self.doSearch(parseInt(start + ipp));
                                });
                            });       
                        }
                    },
                    error : function(data){
                        self.noResults('#ytb-usr-results');
                    }
                }).fail(function() {
                    self.stopLoading('#ytb-src-more');
                    self.noResults('#ytb-usr-results');
                })
            },
            doFavorites: function (start) {
                var self = this;
                var key = $('#youtube-search-text').val();
                if(key == '') {
                    return 1;
                }
                start = typeof start !== 'undefined' ? start : 1;
                this.showLoading('#ytb-fav-more');
                if (start == 1) {
                    $('#ytb-fav-results').html('');
                    self.data = [];
                }
                
                var fullUrl = 'http://gdata.youtube.com/feeds/api/users/'+key+'/favorites?v=2&max-results=20&alt=jsonc&start-index='+start;
                $.ajax({
                    url : fullUrl,
                    dataType: 'json',
                    success : function(myData){
                        self.stopLoading('#ytb-fav-more');
                        var myJson = myData;
                        var results = myJson.data.items;
                        var total = myJson.data.totalItems;
                        var ipp = myJson.data.itemsPerPage;
                        var start = myJson.data.startIndex;
                        
                        if( start == 1 && total == 0) {
                            self.noResults('#ytb-fav-results');
                        } else {
                            $.tmpl('livedesk>providers/youtube/favorite-item', {results : self.cleanContent(results)}, function(e,o) {
                                el = $('#ytb-fav-results').append(o).find('.youtube');
                                BlogAction.get('modules.livedesk.blog-post-publish').done(function(action) {
                                    el.draggable({
                                        revert: 'invalid',
                                        helper: 'clone',
                                        appendTo: 'body',
                                        zIndex: 2700,
                                        clone: true,
                                        start: function(evt, ui) {
                                            item = $(evt.currentTarget);
                                            $(ui.helper).css('width', item.width());
                                            var idx = parseInt($(this).attr('idx'),10);
                                            results[idx].id = results[idx].video.id;
                                            results[idx].uploaded = results[idx].video.uploaded;
                                            $(this).data('data', self.adaptor.universal( results[idx] ));
                                        }   
                                    });
                                }).fail(function(){
                                    el.removeClass('draggable');
                                });
                            });
                        }
                        if (parseInt(start + ipp) < total) {
                            $('#ytb-fav-more').tmpl('livedesk>providers/load-more', {
                                name : 'ytb-fav-load-more'
                            }, function(){
                                $(this).find('[name="ytb-fav-load-more"]').on('click', function(){
                                    self.doFavorites(parseInt(start + ipp));
                                });
                            });       
                        }
                    },
                    error : function(data){
                        self.noResults('#ytb-usr-results');
                    }
                }).fail(function() {
                    self.stopLoading('#ytb-fav-more');
                    self.noResults('#ytb-fav-results');
                });
                
            },
            doUsers: function (start) {
                var self = this;
                var key = $('#youtube-search-text').val();
                if(key == '') {
                    return 1;
                }
                start = typeof start !== 'undefined' ? start : 1;
                
                this.showLoading('#ytb-usr-more');
                if (start == 1) {
                    $('#ytb-usr-results').html('');
                }
                var fullUrl = 'http://gdata.youtube.com/feeds/api/users/'+key+'/uploads?v=2&max-results=20&alt=jsonc&start-index='+start;
                $.ajax({
                    url : fullUrl,
                    dataType: 'json',
                    success : function(myData){
                        self.stopLoading('#ytb-usr-more');
                        var myJson = myData;
                        var results = myJson.data.items;
                        var total = myJson.data.totalItems;
                        var ipp = myJson.data.itemsPerPage;
                        var start = myJson.data.startIndex;
                        
                        if( start == 1 && total == 0) {
                            self.noResults('#ytb-usr-results');
                        } else {
                            $.tmpl('livedesk>providers/youtube/clip-item', {results : self.cleanContent(results)}, function(e,o) {
                                el = $('#ytb-usr-results').append(o).find('.youtube');
                                BlogAction.get('modules.livedesk.blog-post-publish').done(function(action) {
                                    el.draggable({
                                        revert: 'invalid',
                                        helper: 'clone',
                                        appendTo: 'body',
                                        zIndex: 2700,
                                        clone: true,
                                        start: function(evt, ui) {
                                            item = $(evt.currentTarget);
                                            $(ui.helper).css('width', item.width());
                                            var idx = parseInt($(this).attr('idx'),10);
                                            $(this).data('data', self.adaptor.universal( results[idx] ));
                                        }   
                                    });
                                }).fail(function(){
                                    el.removeClass('draggable');
                                });
                            });
                        }
                        
                        if (parseInt(start + ipp) < total) {
                            $('#ytb-usr-more').tmpl('livedesk>providers/load-more', {
                                name : 'ytb-usr-load-more'
                            }, function(){
                                $(this).find('[name="ytb-usr-load-more"]').on('click', function(){
                                    self.doUsers(parseInt(start + ipp));
                                });
                            });       
                        }
                    },
                    error : function(data){
                        self.noResults('#ytb-usr-results');
                    }
                }).fail(function() {
                    self.stopLoading('#ytb-usr-more');
                    self.noResults('#ytb-usr-results');
                });
                
            }		
        });
        return providers;
    });