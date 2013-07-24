/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

define('providers/twitter', [
    'providers',    
    'jquery',
    config.guiJs('livedesk', 'action'),
    'jquery/tmpl',
    'jquery/jsonp',    
    'jqueryui/draggable',
    'providers/twitter/adaptor',
    'tmpl!livedesk>providers/twitter',
    config.guiJs('livedesk', 'providers-templates'),
    'tmpl!livedesk>items/item',
    'tmpl!livedesk>items/implementors/sources/base',
    'tmpl!livedesk>items/implementors/sources/twitter',
    'tmpl!livedesk>providers/load-more',
    'tmpl!livedesk>providers/no-results',
    'tmpl!livedesk>providers/jsonp-error',
    'tmpl!livedesk>providers/loading',
], function( providers,  $, BlogAction ) {
$.extend(providers.twitter, {
        initialized: false,
        //stuff I need for the autorefresh
        refreshTimer : 10000,
        lastTimeline : null,
        //interval Id 
        iidTimeline : -1,
        
        lastUser : null,
        iidUser : -1,
        
        lastFavorites : null,
        iidFavorites : -1,
        
        lastWeb : null,
        iidWeb : -1,
        
        lastSearchItem: '',
        
	data: [],
	init: function(){
        this.notificationButton = $('.'+providers.twitter.className).
            parents('li:eq(0)').
            find('.config-notif');
                
		if(!this.initialized || !this.el.children(":first").length) {
            this.adaptor._parent = this;
            this.adaptor.init();
            this.resetAutoRefresh();            
            localStorage.setItem('superdesk.config.providers.twitter.notify', 0);
		}

		this.initialized = true;

        $('a[href="#twitter"] span.notifications').html('').css('display', 'none');
        
        this.notificationButton.off('click').on('click', this.configNotif);
            
        this.notificationButton.
            attr('title',_('Click to turn notifications on or off <br />while this tab is hidden')).
            tooltip({placement: 'right'});
	},

        /*!
         * configure notifications on/off
         */
        configNotif: function()
        {
            var cnfNotif = localStorage.getItem('superdesk.config.providers.twitter.notify');
            if( !parseFloat(cnfNotif) )
            {
                localStorage.setItem('superdesk.config.providers.twitter.notify', 1);
                $(this).removeClass('badge-info').addClass('badge-warning');
            }
            else
            {
                localStorage.setItem('superdesk.config.providers.twitter.notify', 0);
                $(this).removeClass('badge-warning').addClass('badge-info');
            }
        },
        
        isTwitterActive : function() {
            var twitterTab = $('.big-icon-twitter').closest('li.twitter');
            return twitterTab.hasClass('active');
        },

        resetAutoRefresh : function() {
            this.lastTimeline = null;
            clearTimeout(this.iidTimeline);
            this.iidTimeline = -1;
            
            this.lastUser = null;
            clearTimeout(this.iidUser);
            this.iidUser = -1;
            
            this.lastFavorites = null;
            clearTimeout(this.iidFavorites);
            this.iidFavorites = -1;
            
            this.lastWeb = null;
            clearTimeout(this.iidWeb);
            this.iidWeb = -1;
            
            
        },

	render: function() {
		var self = this;
		this.el.tmpl('livedesk>providers/twitter', {}, function(){
			self.el.on('click', '#twt-search-controls>li', function(evt){
              evt.preventDefault();
			  $(this).siblings().removeClass('active').end().addClass('active');
			  var myArr = $(this).attr('id').split('-');
			  //hide all ggl result holders
			  self.el.find('.scroller').css('visibility', 'hidden');
                          self.el.find('.twitter-search-text').css('display', 'none');
			  //show only the one we need
			  $('#twt-'+myArr[1]+'-holder').css('visibility', 'visible');
                          $('#twitter-search-'+myArr[1]).css('display', 'inline');
			  self.startSearch();
			})
			.on('keyup','.twitter-search-text', function(e){
				if(e.keyCode == 13 && $(this).val().length > 0) {
					//enter press on google search text
					//check what search it is
                                        
					self.startSearch(true);
				}
			});

            self.notificationButton.css('display', '');
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
        startSearch: function(refresh) {
                var self = this;
                refresh = refresh || false;
                if ( $('#twt-web-tab').hasClass('active') ) {
                    self.doWeb(undefined, refresh);
                }
                if ( $('#twt-timeline-tab').hasClass('active') ) {
                    self.doTimeline(1, refresh);
                }
                if ( $('#twt-user-tab').hasClass('active') ) {
                    self.doUser(1, refresh);
                }
                if ( $('#twt-favorites-tab').hasClass('active') ) {
                    self.doFavorites(1, refresh);
                }
        },
        flashThumb : function(from) {
            $('a[href="#twitter"] span.notifications').html('New').css('display', 'inline');
            this.resetAutoRefresh();
        },
        autoRefreshTimeline : function(fullUrl) {
                var self = this;

                this.iddTimeline = setTimeout(function() {
                    self.autoRefreshTimeline(fullUrl);
                }, this.refreshTimer);

                if ( ! this.isTwitterActive() ) {
                    $.jsonp({
                        url : fullUrl,
                        success : function(data){
                            if (data.length > 1) {
                                if (data[0].id_str !== self.lastTimeline.id_str) {
                                    //console.log( data[0],'-',self.lastTimeline );
                                    self.flashThumb('timeline');
                                    self.doTimeline(1, true);
                                } else {
                                //same result do nothing
                                }
                            }
                        }
                    })
                } else {
                    //do nothing
                }
            
            },
            replaceURLWithHTMLLinks: function(text) {
                var exp = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
                return text.replace(exp,"<a href='$1' target='_blank'>$1</a>"); 
            },
            /*!
             * Keep compatibility with the api version 1.0
             */
            adaptOldApiData : function(item) {
                item.profile_image_url = item.user.profile_image_url;
                item.from_user_name = item.user.name;
                item.from_user = item.user.screen_name;
                item.created_at_formated = item.created_at;
                item.api_version = '1.1';
                return item;
            },
        doTimeline: function(page, refresh) {
                var self = this, el;
                
                if ( $('#twitter-search-timeline').val().length < 1) {
                    $('#twitter-search-timeline').val(this.lastSearchItem);
                }
                
                page = page || 1;
                refresh = refresh || false;
                var text = $('#twitter-search-timeline').val();
                if (text.length < 1) {
                    return;
                } else {
                    if (this.lastTimelineSearchItem == text &&  !refresh) {
                        return;
                    }
                    this.lastSearchItem = text;
                    this.lastTimelineSearchItem = text;
                }
                $('#twt-timeline-more').html('');
                if (page == 1) {
                    $('#twt-timeline-results').html('');
                    self.data.timeline = [];
                }
                this.showLoading('#twt-timeline-more');
                self.resetAutoRefresh();
                this.cb.__call(
                    'statuses_userTimeline',
                    'include_rts=true&screen_name='+text+'&page='+page,
                    function(data){
                        self.stopLoading('#twt-timeline-more');
                        var posts = [];
                        for( var item, i = 0, count = data.length; i < count; i++ ){
                            item = self.adaptOldApiData(data[i]);
                            item.type = 'timeline'
                            self.data.timeline[item.id_str] = item;
                            posts.push({ Meta: item });
                        }
                        if (page == 0 && data.length > 0) {
                                self.lastTimeline = data[0];
                                self.iidTimeline = setTimeout(function(){
                                  self.autoRefreshTimeline(fullUrl);  
                                }, self.refreshTimer);
                            }
                        if (data.length > 0 || page > 0) {
                             $.tmpl('livedesk>items/item', { 
                                    Post: posts,
                                    Base: 'implementors/sources/twitter',
                                    Item: 'sources/twitter'
                                }, function(e,o) {
                                    el = $('#twt-timeline-results').append(o).find('.twitter');
                                    BlogAction.get('modules.livedesk.blog-post-publish').done(function(action) {
                                        el.draggable({
                                            addClasses: false,
                                            revert: 'invalid',
                                            helper: 'clone',
                                            appendTo: 'body',
                                            //containment: containment,
                                            zIndex: 2700,
                                            clone: true,
                                            start: function(evt, ui) {
                                                item = $(evt.currentTarget);
                                                $(ui.helper).css('width', item.width());
                                                $(this).data('data', self.adaptor.universal(self.data.timeline[ $(this).attr('id_str') ]));
                                            }

                                        });
                                    }).fail(function(){
                                        el.removeClass('draggable');
                                    });
                            });
                            if (data.length > 19) {
                                $('#twt-timeline-more').tmpl('livedesk>providers/load-more', {name : 'twitter-timeline-load-more'}, function(){
                                    $(this).find('[name="twitter-timeline-load-more"]').on('click', function(){
                                        self.doTimeline(parseInt(page + 2),true);
                                    });
                                });       
                            }
                            
                        } else {
                            self.noResults('#twt-timeline-results');
                        }
                }, true ); // this parameter required
            },
        autoRefreshUser : function(qstring) {
            var self = this;

            this.iidUser = setTimeout(function() {
                self.autoRefreshUser(qstring);
            }, this.refreshTimer);

            if ( this.isTwitterActive() ) {
                return 1;
            }

            self.cb.__call(
                'statuses_userTimeline',
                qstring,
                function(data){
                    if (data.length > 1) {
                        if (data[0].id_str != self.lastUser.id_str) {
                            self.flashThumb('user');
                            self.doUser(1, true);
                        } else {
                            //same result do nothing
                        }
                    }
                }, true);
        },
        doUser : function(page, refresh) {
            page = page || 1;
            refresh = refresh || false;
            var self = this,
                qstring;
            
            if ( $('#twitter-search-user').val() < 1 ){
                $('#twitter-search-user').val(this.lastSearchItem);
            }
            var text = $('#twitter-search-user').val();
            if (text.length < 1) {
                return;
            } else {
                if ( this.lastUserSearchItem == text &&  !refresh) {
                    return;
                }
                this.lastSearchItem = this.lastUserSearchItem = text;
            }
            
            
            if (page == 1) {
                $('#twt-user-results').html('');
                self.data.user = [];
            }
            this.showLoading('#twt-user-more');
            self.resetAutoRefresh();
            qstring = 'screen_name='+text+'&page='+page;
            this.cb.__call(
                'statuses_userTimeline',
                qstring,
                function(data){
                    self.stopLoading('#twt-user-more');
                    var posts = [];
                    for( var item, i = 0, count = data.length; i < count; i++ ){
                        item = self.adaptOldApiData(data[i]);
                        item.type = 'user'
                        self.data.user[item.id_str] = item;
                        posts.push({ Meta: item });
                    }
                    if (page == 1 && data.length > 0) {                   
                            self.lastUser = data[0];
                            self.iidUser = setTimeout(function(){
                                self.autoRefreshUser(qstring);  
                            }, self.refreshTimer);
                        }
                    if (data.length > 0 || page > 1) {
                         $.tmpl('livedesk>items/item', { 
                                Post: posts,
                                Base: 'implementors/sources/twitter',
                                Item: 'sources/twitter'
                            }, function(e,o) {
                                el = $('#twt-user-results').append(o).find('.twitter');
                                BlogAction.get('modules.livedesk.blog-post-publish').done(function(action) {
                                    el.draggable({
                                        addClasses: false,
                                        revert: 'invalid',
                                        helper: 'clone',
                                        appendTo: 'body',
                                        zIndex: 2700,
                                        clone: true,
                                        start: function(evt, ui) {
                                            item = $(evt.currentTarget);
                                            $(ui.helper).css('width', item.width());
                                            $(this).data('data', self.adaptor.universal(self.data.user[ $(this).attr('id_str') ]));
                                        }

                                    });
                                }).fail(function(){
                                    el.removeClass('draggable');
                                });
                        });
                        if (data.length > 19) {
                            $('#twt-user-more').tmpl('livedesk>providers/load-more', {name : 'twitter-user-load-more'}, function(){
                                $(this).find('[name="twitter-user-load-more"]').on('click', function(){
                                    self.doUser(parseInt(page + 1), true)
                                });
                            });
                        }
                    } else {
                        self.noResults('#twt-user-results');
                    }
                },
                true // this parameter required
            );    
        },
        autoRefreshFavorites : function(qstring) {
            var self = this;

            this.iidFavorites = setTimeout(function() {
                self.autoRefreshFavorites(qstring);
            }, this.refreshTimer);

            if ( this.isTwitterActive() ) {
                return 1;
            }

            self.cb.__call(
                'favorites_list',
                qstring,
                function(data){
                    if (data.length > 1) {
                        if (data[0].id_str != self.lastFavorites.id_str) {
                            self.flashThumb('favorites');
                            self.doFavorites(1, true);
                        } else {
                            //same result do nothing
                        }
                    }
                }, true);
        },
        doFavorites : function(page, refresh) {
            page = page || 1;
            refresh = refresh || false;
            var self = this,
                qstring;
            if ( $('#twitter-search-favorites').val() < 1 ){
                $('#twitter-search-favorites').val(this.lastSearchItem);
            }
            var text = $('#twitter-search-favorites').val();
            if (text.length < 1) {
                return;
            } else {
                if ( this.lastFavoritesSearchItem == text &&  !refresh) {
                    return;
                }
                this.lastFavoritesSearchItem = this.lastSearchItem = text;
            }
            page = typeof page !== 'undefined' ? page : 1;
            if( page == 1 ) {
                $('#twt-favorites-results').html('');
                self.data.favorites = [];
            }
            this.showLoading('#twt-favorites-more');
            self.resetAutoRefresh();
            qstring = 'screen_name='+text+'&page='+page;
            this.cb.__call(
                'favorites_list',
                qstring,
                function(data) {
                    self.stopLoading('#twt-favorites-more');
                    var 
                        posts = [];
                    for( var item, i = 0, count = data.length; i < count; i++ ) {
                        item = self.adaptOldApiData(data[i]);
                        item.type = 'favourites'
                        self.data.favorites[item.id_str] = item;
                        posts.push({ Meta: item });
                    }
                    if (page == 1 && data.length > 0) {                   
                            self.lastFavorites = data[0];
                            self.iidFavorites = setTimeout(function(){
                              self.autoRefreshFavorites(qstring);  
                            }, self.refreshTimer);
                        }
                    if (data.length > 0 || page > 1) {
                         $.tmpl('livedesk>items/item', { 
                                Post: posts,
                                Base: 'implementors/sources/twitter',
                                Item: 'sources/twitter'
                            }, function(e,o) {
                                el = $('#twt-favorites-results').append(o).find('.twitter');
                                BlogAction.get('modules.livedesk.blog-post-publish').done(function(action) {
                                    el.draggable({
                                        addClasses: false,
                                        revert: 'invalid',
                                        helper: 'clone',
                                        appendTo: 'body',
                                        zIndex: 2700,
                                        clone: true,
                                        start: function(evt, ui) {
                                            item = $(evt.currentTarget);
                                            $(ui.helper).css('width', item.width());
                                            $(this).data('data', self.adaptor.universal(self.data.favorites[ $(this).attr('id_str') ]));
                                        }

                                    });
                                }).fail(function(){
                                    el.removeClass('draggable');
                                });
                        });
                        //handle load more button
                        if (data.length > 19) {
                            $('#twt-favorites-more').tmpl('livedesk>providers/load-more', {name : 'twitter-favorites-load-more'}, function(){
                                    $(this).find('[name="twitter-favorites-load-more"]').on('click', function(){
                                        self.doFavorites(parseInt(page + 1), true);
                                    });
                            });
                        }
                    } else {
                        self.noResults('#twt-favorites-results');
                    }
                }, true);
        },
        autoRefreshWeb : function(qstring) {
            var self = this;

            this.iidWeb = setTimeout(function() {
                self.autoRefreshWeb(qstring);
            }, this.refreshTimer);

            if (this.isTwitterActive()) {
                return 1;
            }

            this.cb.__call(
                'search_tweets',
                qstring,
                function(data){
                    if (data.statuses.length > 1) {
                        if (data.statuses[0].id_str != self.lastWeb.id_str) {
                            self.flashThumb('web');
                            self.doWeb(qstring, true);
                        } else {
                            //same result do nothing
                        }
                    }
                }, true);
        },
        doWeb : function(qstring, refresh) {
            var skip = qstring || false;
                refresh = refresh || false;
            var self = this;
            var twtVal = $('#twitter-search-web').val();
            if ( twtVal.length < 1  ) {
                $('#twitter-search-web').val(this.lastSearchItem);
            }
            
            var text = $('#twitter-search-web').val();
            if (text.length < 1) {
                return;
            } else {
                if ( this.lastWebSearchItem == text && !refresh ) {
                    return;
                }
                this.lastWebSearchItem = this.lastSearchItem = text;
            }
            
            $('#twt-web-more').html('');

            qstring = typeof qstring !== 'undefined' ? qstring : 'q='+ encodeURIComponent(text) +'&include_entities=true';
            if ( qstring == 'q='+ encodeURIComponent(text) +'&include_entities=true' ) {
                $('#twt-web-results').html('');
                self.data.web = [];
            }
            self.showLoading('#twt-web-more');
            self.resetAutoRefresh();
            self.cb.__call(
                'search_tweets',
                qstring,
                function (data) {
                    self.stopLoading('#twt-web-more');
                    var posts = [];
                    for( var item, i = 0, count = data.statuses.length; i < count; i++ ){
                        item = self.adaptOldApiData(data.statuses[i]);
                        item.type = 'natural'
                        self.data.web[item.id_str] = item;
                        posts.push({ Meta: item });
                    }
                    if ( refresh && posts.length > 0 ) {
                        self.lastWeb = data.statuses[0];
                        self.iidWeb = setTimeout(function(){
                          self.autoRefreshWeb(qstring);
                        }, self.refreshTimer);
                    }
                    if (posts.length > 0) {
                         $.tmpl('livedesk>items/item', { 
                                Post: posts,
                                Base: 'implementors/sources/twitter',
                                Item: 'sources/twitter'
                            }, function(e,o) {
                                el = $('#twt-web-results').append(o).find('.twitter');
                                BlogAction.get('modules.livedesk.blog-post-publish').done(function(action) {
                                    el.draggable({
                                        addClasses: false,
                                        revert: 'invalid',
                                        helper: 'clone',
                                        appendTo: 'body',
                                        zIndex: 2700,
                                        clone: true,
                                        start: function(evt, ui) {
                                            item = $(evt.currentTarget);
                                            $(ui.helper).css('width', item.width());
                                            $(this).data('data', self.adaptor.universal(self.data.web[ $(this).attr('id_str') ]));
                                        }

                                    });
                                }).fail(function(){
                                    el.removeClass('draggable');
                                });
                        });
                        if(data.search_metadata.next_results) {
                            $('#twt-web-more').tmpl('livedesk>providers/load-more', {name : 'twitter-web-load-more'}, function(){
                                    $(this).find('[name="twitter-web-load-more"]').on('click', function(){
                                        self.doWeb(data.search_metadata.next_results, true);
                                    });
                            });
                        }
                    } else {
                        self.noResults('#twt-web-results');
                    }     
                },
                true // this parameter required
            );
        }
});
return providers;
});
