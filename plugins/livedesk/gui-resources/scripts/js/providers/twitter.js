/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

define('providers/twitter', [
    'providers',    
    'jquery',
    'gizmo/superdesk/action',
    'jquery/tmpl',
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
], function( providers,  $, Action ) {
$.extend(providers.twitter, {
        initialized: false,
        urlTimeline : 'http://api.twitter.com/1/statuses/following_timeline.json?callback=?&include_entities=true&include_rts=true&screen_name=%(text)s&page=%(page)s',
        
        urlUser : 'http://api.twitter.com/1/statuses/user_timeline.json?callback=?&include_entities=true&include_rts=true&screen_name=%(text)s&page=%(page)s',
        
        urlFavorites : 'http://api.twitter.com/1/favorites.json?callback=?&screen_name=%(text)s&page=%(page)s',
        
        
        //stuff I need for the autorefresh
        refreshTimer : 3000,
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
		if(!this.initialized || !this.el.children(":first").length) {
			this.render();
                        this.adaptor.init();
                        this.resetAutoRefresh();
                        
		}
		this.initialized = true;
                // thid.notifyArea = $('.'+providers.twitter.className).parents('li:eq(0)').find('.notifications')
                //clear new item notification
                $('a[href="#twitter"] span.notifications').html('').css('display', 'none');
                
                localStorage.setItem('superdesk.config.providers.twitter.notify', 0);
                
                $('.'+providers.twitter.className)
                    .parents('li:eq(0)').find('.config-notif').off('click').on('click', this.configNotif);
            
                $('.'+providers.twitter.className)
                    .parents('li:eq(0)').find('.config-notif')
                    .attr('title',_('Click to turn notifications on or off <br />while this tab is hidden'))
                    .tooltip({placement: 'right'});
                    
                    //console.log('notify-', parseFloat(localStorage.getItem('superdesk.config.providers.twitter.notify')));
                
                
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
            var activeText = $('.big-icon-twitter').parent().parent().attr('class');
            if ( activeText == 'active' || parseFloat(localStorage.getItem('superdesk.config.providers.twitter.notify')) == 0 ) {
                return true;
            } else {
                return false;
            }
        },
        resetAutoRefresh : function() {
            
            this.lastTimeline = null;
            clearInterval(this.iidTimeline);
            this.iidTimeline = -1;
            
            this.lastUser = null;
            clearInterval(this.iidUser);
            this.iidUser = -1;
            
            this.lastFavorites = null;
            clearInterval(this.iidFavorites);
            this.iidFavorites = -1;
            
            this.lastWeb = null;
            clearInterval(this.iidWeb);
            this.iidWeb = -1;
            
            
        },
	render: function() {
		var self = this;
		this.el.tmpl('livedesk>providers/twitter', {}, function(){
			self.el.on('click', '#twt-search-controls>li', function(ev){
			  $(this).siblings().removeClass('active') .end().addClass('active');			  
			  var myArr = $(this).attr('id').split('-');
			  //hide all ggl result holders
			  self.el.find('.scroller').css('visibility', 'hidden');
                          self.el.find('.twitter-search-text').css('display', 'none');
			  //show only the one we need
			  $('#twt-'+myArr[1]+'-holder').css('visibility', 'visible');
                          $('#twitter-search-'+myArr[1]).css('display', 'inline');
			  self.startSearch(true);
			})
			.on('keyup','.twitter-search-text', function(e){
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
        flashThumb : function(from) {
            $('a[href="#twitter"] span.notifications').html('New').css('display', 'inline');
            this.resetAutoRefresh();
            
        },
        autoRefreshTimeline : function(fullUrl) {
                var self = this;
                if ( ! this.isTwitterActive() ) {
                    $.jsonp({
                        url : fullUrl,
                        success : function(data){
                            if (data.length > 1) {
                                if (data[0].id_str !== self.lastTimeline.id_str) {
                                    //console.log( data[0],'-',self.lastTimeline );
                                    self.flashThumb('timeline');
                                    clearInterval(self.iidTimeline);
                                    self.doTimeline();
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
            adaptUserData : function(data) {
                for ( var i = 0; i < data.length; i ++) {
                    data[i].profile_image_url = data[i].user.profile_image_url;
                    data[i].from_user_name = data[i].user.name;
                    data[i].from_user = data[i].user.screen_name;
                }
                return data;
            },
        doTimeline: function(page) {
                var self = this, el;
                
                if ( $('#twitter-search-timeline').val().length < 1) {
                    $('#twitter-search-timeline').val(this.lastSearchItem);
                }
                
                page = typeof page !== 'undefined' ? page : 1;
                var text = $('#twitter-search-timeline').val();
                if (text.length < 1) {
                    return;
                } else {
                    if (this.lastTimelineSearchItem == text && page == 1) {
                        return;
                    }
                    this.lastSearchItem = text;
                    this.lastTimelineSearchItem = text;
                }
                $('#twt-timeline-more').html('');
                page = typeof page !== 'undefined' ? page : 1;
                if (page == 1) {
                    $('#twt-timeline-results').html('');
                    self.data = [];
                }
                this.showLoading('#twt-timeline-more');
                self.resetAutoRefresh();
                var fullUrl = str.format(this.urlTimeline,{text: encodeURIComponent(text), page: page});
                $.jsonp({
                    url : fullUrl,
                    success : function(data){
                        self.stopLoading('#twt-timeline-more');
                        self.data = self.data.concat(data);
                        
                        
                        var res = {
                            results : self.adaptUserData(data),
                            page : parseInt(page - 1),
                            ipp : 20
                        };
                        
                        if (page == 1 && data.length > 0) {
                            self.lastTimeline = data[0];
                            self.iidTimeline = setInterval(function(){
                              self.autoRefreshTimeline(fullUrl);  
                            }, self.refreshTimer);
                        }
                        
                        if ( data.length > 0 || page > 1) {
                            $.tmpl('livedesk>providers/twitter/user-item', res, function(e,o) {
                                el = $('#twt-timeline-results').append(o).find('.twitter');
                                Action.get('modules.livedesk.blog-post-publish').done(function(action) {
                                    el.draggable({revert: 'invalid',helper: 'clone',appendTo: 'body',zIndex: 2700,clone: true,
                                        start: function(evt, ui) {
                                            item = $(evt.currentTarget);
                                            $(ui.helper).css('width', item.width());
                                            $(this).data('data', self.adaptor.universal( $(this) ));
                                            var idx = parseInt($(this).attr('idx'),10), page = parseInt($(this).attr('page'),10), ipp = parseInt($(this).attr('ipp'),10);
                                            var itemNo = parseInt( (page * ipp) + idx );
                                            self.data[itemNo].type = 'user';
                                            $(this).data('data', self.adaptor.universal(self.data[ itemNo ]));
                                        }   
                                    });
                                }).fail(function(){
                                    el.removeClass('draggable');
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
                        self.stopLoading('#twt-timeline-more');
                        self.noResults('#twt-timeline-results');
                        self.resetAutoRefresh();
                    }
                })
            },
        autoRefreshUser : function(fullUrl) {
            var self = this;
            if ( this.isTwitterActive() ) {
                return 1;
            }
            $.jsonp({
                url : fullUrl,
                success : function(data){
                    if (data.length > 1) {
                        if (data[0].id_str != self.lastUser.id_str) {
                            console.log(data[0], ' ',self.lastUser);
                            self.flashThumb('user');
                            clearInterval(self.iidUser);
                            self.doUser();
                        } else {
                            //same result do nothing
                        }
                    }
                }
            })
        },
        doUser : function(page) {
            var self = this;
            
            if ( $('#twitter-search-user').val() < 1 ){
                $('#twitter-search-user').val(this.lastSearchItem);
            }
            page = typeof page !== 'undefined' ? page : 1;
            var text = $('#twitter-search-user').val();
            if (text.length < 1) {
                return;
            } else {
                if ( this.lastUserSearchItem == text && page == 1) {
                    return;
                }
                this.lastSearchItem = this.lastUserSearchItem = text;
            }
            
            
            if (page == 1) {
                $('#twt-user-results').html('');
                self.data = [];
            }
            this.showLoading('#twt-user-more');
            self.resetAutoRefresh();
            var fullUrl = str.format(this.urlUser,{text: encodeURIComponent(text), page: page});
            $.jsonp({
                url : fullUrl,
                success : function(data){
                    self.stopLoading('#twt-user-more');
                    self.data = self.data.concat(data);
                    var res = {
                        results : self.adaptUserData(data),
                        page : parseInt(page - 1),
                        ipp : 20
                    };
                    
                    if (page == 1 && data.length > 0) {
                        
                            self.lastUser = data[0];
                            self.iidUser = setInterval(function(){
                              self.autoRefreshUser(fullUrl);  
                            }, self.refreshTimer);
                        }
                    
                    if (data.length > 0 || page > 1) {
                        $.tmpl('livedesk>providers/twitter/user-item', res, function(e,o) {
                            el = $('#twt-user-results').append(o).find('.twitter');
                            Action.get('modules.livedesk.blog-post-publish').done(function(action) {
                                el.draggable({revert: 'invalid',helper: 'clone',appendTo: 'body',zIndex: 2700,clone: true,
                                    start: function(evt, ui) {
                                        item = $(evt.currentTarget);
                                        $(ui.helper).css('width', item.width());
                                        var idx = parseInt($(this).attr('idx'),10), page = parseInt($(this).attr('page'),10), ipp = parseInt($(this).attr('ipp'),10);
                                        var itemNo = parseInt( (page * ipp) + idx );
                                        self.data[itemNo].type = 'user';
                                        $(this).data('data', self.adaptor.universal(self.data[ itemNo ]));
                                    }   
                                });
                            }).fail(function(){
                                el.removeClass('draggable');
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
                    self.stopLoading('#twt-user-more');
                    self.noResults('#twt-user-results');
                    self.resetAutoRefresh();
                }
            });
            
        },
        autoRefreshFavorites : function(fullUrl) {
            if ( this.isTwitterActive() ) {
                return 1;
            }
            var self = this;
            $.jsonp({
                url : fullUrl,
                success : function(data){
                    if (data.length > 1) {
                        if (data[0].id_str != self.lastFavorites.id_str) {
                            self.flashThumb('favorites');
                            clearInterval(self.iidFavorites);
                        } else {
                            //same result do nothing
                        }
                    }
                }
            })
        },
        doFavorites : function(page) {
            var self = this;
            if ( $('#twitter-search-favorites').val() < 1 ){
                $('#twitter-search-favorites').val(this.lastSearchItem);
            }
            page = typeof page !== 'undefined' ? page : 1;
            var text = $('#twitter-search-favorites').val();
            if (text.length < 1) {
                return;
            } else {
                if ( this.lastFavoritesSearchItem == text && page == 1) {
                    return;
                }
                this.lastFavoritesSearchItem = this.lastSearchItem = text;
            }
            page = typeof page !== 'undefined' ? page : 1;
            if( page == 1 ) {
                $('#twt-favorites-results').html('');
                self.data = [];
            }
            this.showLoading('#twt-favorites-more');
            var fullUrl = str.format(this.urlFavorites,{text: encodeURIComponent(text), page: page});
            self.resetAutoRefresh();
            $.jsonp({
                url: fullUrl,
                success : function(data) {
                    self.stopLoading('#twt-favorites-more');
                    self.data = self.data.concat(data);
                    var res = {
                        results : self.adaptUserData(data),
                        page : parseInt(page - 1),
                        ipp : 20
                    };
                    
                    if (page == 1 && data.length > 0) {
                            self.lastFavorites = data[0];
                            self.iidUser = setInterval(function(){
                              self.autoRefreshFavorites(fullUrl);  
                            }, self.refreshTimer);
                        }
                    
                    if (data.length > 0 || page > 1) {
                        //feed results to template
                        $.tmpl('livedesk>providers/twitter/user-item', res, function(e,o) {
                            el = $('#twt-favorites-results').append(o).find('.twitter');
                            Action.get('modules.livedesk.blog-post-publish').done(function(action) {
                                el.draggable({revert: 'invalid',helper: 'clone',appendTo: 'body',zIndex: 2700,clone: true,
                                    start: function(evt, ui) {
                                        item = $(evt.currentTarget);
                                        $(ui.helper).css('width', item.width());
                                        var idx = parseInt($(this).attr('idx'),10), page = parseInt($(this).attr('page'),10), ipp = parseInt($(this).attr('ipp'),10);
                                        var itemNo = parseInt( (page * ipp) + idx );
                                        self.data[itemNo].type = 'user';
                                        $(this).data('data', self.adaptor.universal(self.data[ itemNo ]));
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
                                        self.doFavorites(parseInt(page + 1));
                                    });
                            });
                        }
                    } else {
                        self.noResults('#twt-favorites-results');
                    }
                },
                error : function(xOptions, message) {
                    self.stopLoading('#twt-favorites-more');
                    self.noResults('#twt-favorites-results');
                    self.resetAutoRefresh();
                }
            });
        },
        autoRefreshWeb : function(fullUrl) {
            if ( this.isTwitterActive() ) {
                return 1;
            }
            var self = this;
            $.jsonp({
                url : fullUrl,
                success : function(data){
                    if (data.results.length > 1) {
                        if (data.results[0].id_str != self.lastWeb.id_str) {
                            self.flashThumb('web');
                            clearInterval(self.iidWeb);
                            self.doWeb();
                        } else {
                            //same result do nothing
                        }
                    }
                }
            })
        },
        doWeb : function(qstring) {
            
            var skip = false;
            if ( typeof qstring == 'undefined' ) {
                skip = true;
            }
            
            var self = this;
            var twtVal = $('#twitter-search-web').val();
            if ( twtVal.length < 1  ) {
                $('#twitter-search-web').val(this.lastSearchItem);
            }
            
            var text = $('#twitter-search-web').val();
            if (text.length < 1) {
                return;
            } else {
                if ( this.lastWebSearchItem == text && skip ) {
                    return;
                }
                this.lastWebSearchItem = this.lastSearchItem = text;
            }
            
            $('#twt-web-more').html('');

            qstring = typeof qstring !== 'undefined' ? qstring : '?q='+ encodeURIComponent(text) +'&include_entities=true';
            if ( qstring == '?q='+ encodeURIComponent(text) +'&include_entities=true' ) {
                $('#twt-web-results').html('');
                self.data = [];
            }

            var mainUrl = 'http://search.twitter.com/search.json';
            var url = mainUrl + qstring + '&result_type=recent&callback=?';
            this.showLoading('#twt-web-more');
            self.resetAutoRefresh();
            $.jsonp({
               url : url,
               success : function(data){
                    
                    self.data = self.data.concat(data.results);
                    self.stopLoading('#twt-web-more');
                    var res = {
                        results : data.results,
                        page : parseInt(data.page - 1),
                        ipp : parseInt(data.results_per_page)
                    };
                    
                    if (res.page == 0 && data.results.length > 0) {
                            self.lastWeb = data.results[0];
                            self.iidWeb = setInterval(function(){
                              self.autoRefreshWeb(url);  
                            }, self.refreshTimer);
                        }
                    if (data.results.length > 0) {
                        $.tmpl('livedesk>providers/twitter/web-item', res, function(e,o) {
                                el = $('#twt-web-results').append(o).find('.twitter');
                                Action.get('modules.livedesk.blog-post-publish').done(function(action) {
                                    el.draggable({
                                        revert: 'invalid',
                                        helper: 'clone',
                                        appendTo: 'body',
                                        zIndex: 2700,
                                        clone: true,
                                        start: function(evt, ui) {
                                            item = $(evt.currentTarget);
                                            $(ui.helper).css('width', item.width());
                                            var idx = parseInt($(this).attr('idx'),10), page = parseInt($(this).attr('page'),10), ipp = parseInt($(this).attr('ipp'),10);
                                            var itemNo = parseInt( (page * ipp) + idx );
                                            self.data[itemNo].type = 'natural';
                                            $(this).data('data', self.adaptor.universal(self.data[ itemNo ]));
                                        }   
                                    });
                                }).fail(function(){
                                    el.removeClass('draggable');
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
                self.stopLoading('#twt-web-more');
                self.jsonpError('#twt-web-more');
                self.resetAutoRefresh();
            }
            });
        }
});
return providers;
});