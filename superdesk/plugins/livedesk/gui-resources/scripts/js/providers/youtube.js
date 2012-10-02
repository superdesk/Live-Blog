/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

define('providers/youtube', [
    'providers','utils/str', 
    'jquery','jquery/tmpl',
    'jqueryui/draggable',
    'providers/youtube/adaptor',
    'tmpl!livedesk>providers/youtube',
    'tmpl!livedesk>providers/youtube/clip-item',
    'tmpl!livedesk>providers/google-more',
    'tmpl!livedesk>providers/no-results',
    'tmpl!livedesk>providers/loading'
    ], function( providers, str, $ ) {
        $.extend(providers.youtube, {
            initialized: false,
            url: 'https://ajax.youtubeapis.com/ajax/services/search/%(type)s?v=1.0&start=%(start)s&q=%(text)s&callback=?',
            urls: {
                web: '',
                news: '',
                images: ''
            },
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
                if ( $('#ytb-src-tab').hasClass('active') ) {
                    //do youtube search
                    if (fresh || $('#ytb-src-results').html() == '') {
                        self.doSearch();
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
            doSearch: function (start) {
                var self = this;
                var key = $('youtube-search-text').val();
                
            },
            doFavorites: function (start) {
                var self = this;
                
            },
            doUsers: function (start) {
                var self = this;
                
            }		
        });
        return providers;
    });