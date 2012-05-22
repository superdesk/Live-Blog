/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

define('providers/twitter', [
    'providers',
    'jquery','jquery/tmpl',
    'jqueryui/draggable',
    'tmpl!livedesk>providers/twitter',
    'tmpl!livedesk>providers/twitter/user-item',
    'tmpl!livedesk>providers/twitter/web-item',
    'tmpl!livedesk>providers/load-more',
    'tmpl!livedesk>providers/no-results',
    'jquery'
], function( providers,  $ ) {
$.extend(providers.twitter, {
        initialized: false,
        urlTimeline : 'http://api.twitter.com/1/statuses/following_timeline.json?callback=?&include_entities=true&include_rts=true&screen_name=%(text)s&count=%(count)s',
        urlUser : 'http://api.twitter.com/1/statuses/user_timeline.json?callback=?&include_entities=true&include_rts=true&screen_name=%(text)s&count=%(count)s',
        urlFavorites : 'http://api.twitter.com/1/favorites.json?callback=?&screen_name=%(text)s&count=%(count)s',
	data: [],
	init: function(){
                //console.log('twitter main init');
		if(!this.initialized) {
			this.render();
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
                    self.doFavorites();
                }
        },
        doTimeline: function(count) {
            var self = this;
            var text = escape($('#twitter-search-text').val());
    
            if (text.length < 1) {
                return;
            }
            $('#twt-timeline-more').html('');

            count = typeof count !== 'undefined' ? count : parseInt(8);
            $('#twt-timeline-results').html('');

            $.getJSON(str.format(this.urlTimeline,{text: text, count: count}), {}, function(data){
                    //console.log(data);
                    var usrData = {
                        results: data
                    }
                    if ( data.length > 0 ) {
                        $.tmpl('livedesk>providers/twitter/user-item', usrData, function(e,o) {
                            $('#twt-timeline-results').append(o).find('.twitter').draggable({ containment:'document', helper: 'clone', appendTo: 'body', zIndex: 2700});
                        });			


                        var countmore = parseInt(count) + 8;
                        var loadMore = {
                            name : 'twitter-timeline-load-more'
                        }
                        $('#twt-timeline-more').tmpl('livedesk>providers/load-more', loadMore, function(){
                            $(this).find('[name="twitter-timeline-load-more"]').on('click', function(){
                                self.doTimeline(countmore);
                            });
                        });       
                    } else {
                        $.tmpl('livedesk>providers/no-results', data.responseData, function(e,o) {
                            $('#twt-timeline-results').append(o);
                        });
                    }
                    
            });

        },
        doUser : function(count) {
            var self = this;
            var text = escape($('#twitter-search-text').val());
    
            if (text.length < 1) {
                return;
            }
            $('#twt-user-more').html('');

            count = typeof count !== 'undefined' ? count : parseInt(8);
            $('#twt-user-results').html('');

            $.getJSON(str.format(this.urlUser,{text: text, count: count}), {}, function(data){
                    var usrData = {
                        results: data
                    }
                    
                    if (data.length > 0) {
                        $.tmpl('livedesk>providers/twitter/user-item', usrData, function(e,o) {
                            $('#twt-user-results').append(o).find('.twitter').draggable({ containment:'document', helper: 'clone', appendTo: 'body', zIndex: 2700});
                        });			


                        var countmore = parseInt(count + 8);
                        var loadMore = {
                            name : 'twitter-user-load-more'
                        }

                        $('#twt-user-more').tmpl('livedesk>providers/load-more', loadMore, function(){
                                $(this).find('[name="twitter-user-load-more"]').on('click', function(){
                                    self.doUser(countmore)
                                });
                        });
                    } else {
                        $.tmpl('livedesk>providers/no-results', data.responseData, function(e,o) {
                            $('#twt-user-results').append(o);
                        });
                    }
                    
                    
            });

        },
        doFavorites : function(count) {
            var self = this;
            var text = escape($('#twitter-search-text').val());
    
            if (text.length < 1) {
                return;
            }
            $('#twt-favorites-more').html('');

            count = typeof count !== 'undefined' ? count : parseInt(8);
            $('#twt-favorites-results').html('');

            $.getJSON(str.format(this.urlFavorites,{text: text, count: count}), {}, function(data){
                    var usrData = {
                        results: data
                    }
                    
                    
                    
                    if (data.length > 0) {
                        $.tmpl('livedesk>providers/twitter/user-item', usrData, function(e,o) {
                            $('#twt-favorites-results').append(o).find('.twitter').draggable({ containment:'document', helper: 'clone', appendTo: 'body', zIndex: 2700});
                        });			


                        var countmore = parseInt(count + 8);
                        var loadMore = {
                            name : 'twitter-favorites-load-more'
                        }

                        $('#twt-favorites-more').tmpl('livedesk>providers/load-more', loadMore, function(){
                                $(this).find('[name="twitter-favorites-load-more"]').on('click', function(){
                                    self.doFavorites(countmore)
                                });
                        });
                    } else {
                        $.tmpl('livedesk>providers/no-results', data.responseData, function(e,o) {
                            $('#twt-favorites-results').append(o);
                        });
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

            qstring = typeof qstring !== 'undefined' ? qstring : '?q='+ text +'&rpp=5&include_entities=true';
            if ( qstring == '?q='+ text +'&rpp=5&include_entities=true' ) {
                $('#twt-web-results').html('');
            }

            var mainUrl = 'http://search.twitter.com/search.json';
            var url = mainUrl + qstring + '&result_type=mixed&callback=?';

            $.getJSON(url, {}, function(data){
                    if (data.results.length > 0) {
                        $.tmpl('livedesk>providers/twitter/web-item', data, function(e,o) {
                                $('#twt-web-results').append(o).find('.twitter').draggable({ containment:'document', helper: 'clone', appendTo: 'body', zIndex: 2700});
                        });			

                        var loadMore = {
                            name : 'twitter-web-load-more'
                        }

                        if (data.next_page) {
                            $('#twt-web-more').tmpl('livedesk>providers/load-more', loadMore, function(){
                                    $(this).find('[name="twitter-web-load-more"]').on('click', function(){
                                        self.doWeb(data.next_page)
                                    });
                            });
                        }
                    } else {
                        $.tmpl('livedesk>providers/no-results', data.responseData, function(e,o) {
                            $('#twt-web-results').append(o);
                        });	
                    }
                    
                    
            });

        }
});
return providers;
});