/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

define('providers/youtube', [
    'providers','utils/str', 
    'jquery','jquery/tmpl','jquery/jsonp',
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
    ], function( providers, str, $ ) {
        $.extend(providers.youtube, {
            initialized: false,
            data: [],
            init: function(){
                if(!this.initialized) {
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
                    });
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
                    $(where).append(o);
                });
            },
            doSearch: function (start) {
                var self = this;
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
                            $.tmpl('livedesk>providers/youtube/clip-item', {results : results}, function(e,o) {
                                $('#ytb-src-results').append(o).find('.youtube').draggable({
                                    revert: 'invalid',
                                    helper: 'clone',
                                    appendTo: 'body',
                                    zIndex: 2700,
                                    clone: true,
                                    start: function() {
                                        var idx = parseInt($(this).attr('idx'),10);
                                        self.adaptor.universal(results[idx]);
                                    }   
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
                            $.tmpl('livedesk>providers/youtube/favorite-item', {results : results}, function(e,o) {
                                $('#ytb-fav-results').append(o).find('.youtube').draggable({
                                    revert: 'invalid',
                                    helper: 'clone',
                                    appendTo: 'body',
                                    zIndex: 2700,
                                    clone: true,
                                    start: function() {
                                        $(this).data('data', self.adaptor.universal( $(this) ));
                                        var idx = parseInt($(this).attr('idx'),10), page = parseInt($(this).attr('page'),10), ipp = parseInt($(this).attr('ipp'),10);
                                        var itemNo = parseInt( (page * ipp) + idx );
                                        //self.data[itemNo].type = 'user';
                                        //$(this).data('data', self.adaptor.universal(self.data[ itemNo ]));
                                    }   
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
                })
                
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
                            $.tmpl('livedesk>providers/youtube/clip-item', {results : results}, function(e,o) {
                                $('#ytb-usr-results').append(o).find('.youtube').draggable({
                                    revert: 'invalid',
                                    helper: 'clone',
                                    appendTo: 'body',
                                    zIndex: 2700,
                                    clone: true,
                                    start: function() {
                                        $(this).data('data', self.adaptor.universal( $(this) ));
                                        var idx = parseInt($(this).attr('idx'),10), page = parseInt($(this).attr('page'),10), ipp = parseInt($(this).attr('ipp'),10);
                                        var itemNo = parseInt( (page * ipp) + idx );
                                        //self.data[itemNo].type = 'user';
                                        //$(this).data('data', self.adaptor.universal(self.data[ itemNo ]));
                                    }   
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
                })
                
            }		
        });
        return providers;
    });