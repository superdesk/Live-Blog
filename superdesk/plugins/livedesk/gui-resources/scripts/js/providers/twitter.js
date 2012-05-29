/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

define('providers/twitter', [
    'providers',    
    'jquery','jquery/tmpl',
    'jquery/jsonp',    
    'jqueryui/draggable',
    'providers/twitter/adaptor',
    'tmpl!livedesk>providers/twitter',
    'tmpl!livedesk>providers/twitter/user-item',
    'tmpl!livedesk>providers/twitter/web-item',
    'tmpl!livedesk>providers/load-more',
    'tmpl!livedesk>providers/no-results',
    'tmpl!livedesk>providers/jsonp-error',
    'tmpl!livedesk>providers/loading',
], function( providers,  $ ) {
$.extend(providers.twitter, {
        initialized: false,
        urlTimeline : 'http://api.twitter.com/1/statuses/following_timeline.json?callback=?&include_entities=true&include_rts=true&screen_name=%(text)s&page=%(page)s',
        
        urlUser : 'http://api.twitter.com/1/statuses/user_timeline.json?callback=?&include_entities=true&include_rts=true&screen_name=%(text)s&page=%(page)s',
        
        urlFavorites : 'http://api.twitter.com/1/favorites.json?callback=?&screen_name=%(text)s&page=%(page)s',
        
	data: [],
	init: function(){
                //console.log('twitter main init');
		if(!this.initialized) {
			this.render();
                        this.adaptor.init();
		}
		this.initialized = true;
	},
	render: function() {
		var self = this;
		this.el.tmpl('livedesk>providers/twitter', {}, function(){
			self.el.on('click', '#twt-search-controls>li', function(ev){
			  $(this).siblings().removeClass('active') .end().addClass('active');			  
			  var myArr = $(this).attr('id').split('-');
			  //hide all ggl result holders
			  self.el.find('.scroller').css('visibility', 'hidden');
			  //show only the one we need
			  $('#twt-'+myArr[1]+'-holder').css('visibility', 'visible');
			  self.startSearch(true);
			})
			.on('keyup','#twitter-search-text', function(e){
				if(e.keyCode == 13 && $(this).val().length > 0) {
					//enter press on google search text
					//check what search it is
					self.startSearch(true);
				}
			});
		});  
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
        jsonpError : function(where) {
            $.tmpl('livedesk>providers/jsonp-error', {}, function(e,o) {
                $(where).html(o);
            });
        },
        startSearch: function(fresh) {
                var self = this;
                fresh = typeof fresh !== 'undefined' ? fresh : false;
                if ( $('#twt-web-tab').hasClass('active') ) {
                    self.doWeb();
                }
                if ( $('#twt-timeline-tab').hasClass('active') ) {
                    self.doTimeline();
                }
                if ( $('#twt-user-tab').hasClass('active') ) {
                    self.doUser();

                }
                if ( $('#twt-favorites-tab').hasClass('active') ) {
                    self.doFavorites(1);
                }
        },
        doTimeline: function(page) {
                var self = this;
                var text = escape($('#twitter-search-text').val());
                if (text.length < 1) {
                    return;
                }
                $('#twt-timeline-more').html('');
                page = typeof page !== 'undefined' ? page : 1;
                if (page == 1) {
                    $('#twt-timeline-results').html('');
                }
                this.showLoading('#twt-timeline-more');
                var fullUrl = str.format(this.urlTimeline,{text: text, page: page});
                $.jsonp({
                    url : fullUrl,
                    success : function(data){
                        self.stopLoading('#twt-timeline-more');
                        if ( data.length > 0 || page > 1) {
                            $.tmpl('livedesk>providers/twitter/user-item', {results: data}, function(e,o) {
                                $('#twt-timeline-results').append(o).find('.twitter').draggable({revert: 'invalid',containment:'document',helper: 'clone',appendTo: 'body',zIndex: 2700,clone: true,
                                    start: function() {
                                        $(this).data('data', self.adaptor.universal( $(this) ));
                                    }   
                                });
                            });
                            if (data.length > 19) {
                                $('#twt-timeline-more').tmpl('livedesk>providers/load-more', {name : 'twitter-timeline-load-more'}, function(){
                                    $(this).find('[name="twitter-timeline-load-more"]').on('click', function(){
                                        self.doTimeline(parseInt(page + 1));
                                    });
                                });       
                            }
                            
                        } else {
                            self.noResults('#twt-timeline-results');
                        }
                    },
                    error : function(){
                        self.jsonpError('#twt-timeline-more');
                    }
                })
            },
        doUser : function(page) {
            var self = this;
            var text = escape($('#twitter-search-text').val());
            if (text.length < 1) {
                return;
            }
            
            page = typeof page !== 'undefined' ? page : 1;
            if (page == 1) {
                $('#twt-user-results').html('');
            }
            this.showLoading('#twt-user-more');
            var fullUrl = str.format(this.urlUser,{text: text, page: page});
            $.jsonp({
                url : fullUrl,
                success : function(data){
                    self.stopLoading('#twt-user-more');
                    if (data.length > 0 || page > 1) {
                        $.tmpl('livedesk>providers/twitter/user-item', {results: data}, function(e,o) {
                            $('#twt-user-results').append(o).find('.twitter').draggable({revert: 'invalid',containment:'document',helper: 'clone',appendTo: 'body',zIndex: 2700,clone: true,
                                start: function() {
                                    $(this).data('data', self.adaptor.universal( $(this) ));
                                }   
                            });
                        });			
                        
                        if (data.length > 19) {
                            $('#twt-user-more').tmpl('livedesk>providers/load-more', {name : 'twitter-user-load-more'}, function(){
                                $(this).find('[name="twitter-user-load-more"]').on('click', function(){
                                    self.doUser(parseInt(page + 1))
                                });
                            });
                        }
                    } else {
                        self.noResults('#twt-user-results');
                    }
                },
                error : function() {
                    self.jsonpError('#twt-user-more');
                }
            });
            
        },
        doFavorites : function(page) {
            var self = this;
            var text = escape($('#twitter-search-text').val());
            if (text.length < 1) {
                return;
            }
            page = typeof page !== 'undefined' ? page : 1;
            if( page == 1 ) {
                $('#twt-favorites-results').html('');
            }
            this.showLoading('#twt-favorites-more');
            var fullUrl = str.format(this.urlFavorites,{text: text, page: page});
            $.jsonp({
                url: fullUrl,
                success : function(data) {
                    self.stopLoading('#twt-favorites-more');
                    if (data.length > 0 || page > 1) {
                        //feed results to template
                        $.tmpl('livedesk>providers/twitter/user-item', {results: data}, function(e,o) {
                            $('#twt-favorites-results').append(o).find('.twitter').draggable({revert: 'invalid',containment:'document',helper: 'clone',appendTo: 'body',zIndex: 2700,clone: true,
                                start: function() {
                                    $(this).data('data', self.adaptor.universal( $(this) ));
                                }   
                            });
                        });
                        //handle load more button
                        if (data.length > 19) {
                            $('#twt-favorites-more').tmpl('livedesk>providers/load-more', {name : 'twitter-favorites-load-more'}, function(){
                                    $(this).find('[name="twitter-favorites-load-more"]').on('click', function(){
                                        self.doFavorites(parseInt(page + 1));
                                    });
                            });
                        }
                    } else {
                        self.noResults('#twt-favorites-results');
                    }
                },
                error : function(xOptions, message) {
                    self.jsonpError('#twt-favorites-more');
                }
            });
        },
        doWeb : function(qstring) {
            var self = this;
            var text = escape($('#twitter-search-text').val());
            if (text.length < 1) {
                return;
            }
            $('#twt-web-more').html('');

            qstring = typeof qstring !== 'undefined' ? qstring : '?q='+ text +'&include_entities=true';
            if ( qstring == '?q='+ text +'&include_entities=true' ) {
                $('#twt-web-results').html('');
            }

            var mainUrl = 'http://search.twitter.com/search.json';
            var url = mainUrl + qstring + '&result_type=mixed&callback=?';
            this.showLoading('#twt-web-more');
            
            
            $.jsonp({
               url : url,
               success : function(data){
                    self.stopLoading('#twt-web-more');
                    if (data.results.length > 0) {
                        $.tmpl('livedesk>providers/twitter/web-item', data, function(e,o) {
                                $('#twt-web-results').append(o).find('.twitter').draggable(
                                {
                                    revert: 'invalid',
                                    containment:'document',
                                    helper: 'clone',
                                    appendTo: 'body',
                                    zIndex: 2700,
                                    clone: true,
                                    start: function() {
                                        $(this).data('data', self.adaptor.universal( $(this) ));
                                    }   
                                });
                        });			
                        if (data.next_page) {
                            $('#twt-web-more').tmpl('livedesk>providers/load-more', {name : 'twitter-web-load-more'}, function(){
                                    $(this).find('[name="twitter-web-load-more"]').on('click', function(){
                                        self.doWeb(data.next_page)
                                    });
                            });
                        }
                    } else {
                        self.noResults('#twt-web-results');
                    }
            },
            error : function() {
                self.jsonpError('#twt-web-more');
            }
            });
        }
});
return providers;
});