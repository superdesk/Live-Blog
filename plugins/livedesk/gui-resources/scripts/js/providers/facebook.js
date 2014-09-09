define('providers/facebook', [
    'providers',
    'providers/common',
    'jquery',
    config.guiJs('livedesk', 'action'),    
    'jquery/jsonp',
    'jquery/tmpl',
    'jqueryui/draggable',
    'providers/facebook/adaptor',
    config.guiJs('livedesk', 'providers-templates'),
    'tmpl!livedesk>items/item',
    'tmpl!livedesk>items/implementors/sources/base',
    'tmpl!livedesk>items/implementors/sources/facebook',
    'tmpl!livedesk>providers/facebook',
    'tmpl!livedesk>providers/facebook/item',
    'tmpl!livedesk>providers/facebook/connect',
    'tmpl!livedesk>providers/load-more',
    'tmpl!livedesk>providers/no-results',
    'tmpl!livedesk>providers/loading'
    ], function( providers, common, $, BlogAction) {
        $.extend(providers.facebook, common, {
            appId: 0,
            token: '',
            tokenInterval: 0,
            tokenRefreshTime: 3000,         
            data: [],
            init : function(author, appId) {
                if(!this.initialized || !this.el.children(":first").length) {
                    //this.render();
                    this.adaptor._parent = this;
                    this.adaptor.init(author, appId);
                }
                this.initialized = true;
            },
            fbInit: function() {
                var self = this;
                FB.init({
                    appId      : self.appId,                        // App ID from the app dashboard
                    status     : true,                                 // Check Facebook Login status
                    xfbml      : true                                  // Look for social plugins on the page
                });
            },
            loadFbConnect: function(appId) {
                var self = this;
                self.appId = appId;
                if ( typeof(FB) != 'undefined' ) {
                    self.fbInit();
                    self.fbConnect();
                } else {
                    window.fbAsyncInit = function() {
                        self.fbInit();
                        self.fbConnect();
                    };
                    require(['facebook-connect']);
                }
            },
            fbConnect: function(){
                var self = this;
                FB.getLoginStatus(function(response) {
                    if (response.status === 'connected') {
                        self.token = response.authResponse.accessToken;
                        self.render();
                    } else if (response.status === 'not_authorized') {
                        //not authorized
                        self.fbLogin();
                    } else {
                        //not logged in to facebook
                        self.fbLogin();
                    }
                });
            },
            fbLogin: function() {
                var self = this;
                this.el.tmpl('livedesk>providers/facebook/connect', {}, function() {
                    self.el.off('click','#connect-with-facebook').off('click').on('click','#connect-with-facebook', function(e){
                        FB.login(function(response) {
                            if (response.authResponse) {
                                self.token = response.authResponse.accessToken;
                                self.render();
                            }
                        });
                    })
                });
            },
            refreshToken: function() {
                FB.getLoginStatus(function(response) {
                    if (response.status === 'connected') {
                        self.token = response.authResponse.accessToken;
                    } else if (response.status === 'not_authorized') {
                        //not authorized
                        self.fbLogin();
                    } else {
                        //not logged in to facebook
                        self.fbLogin();
                    }
                }); 
            },
            render: function() {
                var self = this;

                //set an interval to refresh the authToken
                if ( self.tokenInterval ) {
                    window.clearInterval(self.tokenInterval);
                }
                self.tokenInterval = window.setInterval(function(){
                    self.refreshToken();
                }, self.tokenRefreshTime);

                self.el.off('click', '#fbk-search-controls>li').on('click', '#fbk-search-controls>li', function(evt){
                    evt.preventDefault();
                    $(this).siblings().removeClass('active') .end().addClass('active');             
                    var selected = $(this).attr('data-fbktab');
                    if ( selected == 'fb-logout' ) {
                        FB.logout(function(response) {
                            window.clearInterval(self.tokenInterval);
                            self.fbConnect();
                        });
                    };
                    self.el.find('[data-fbkholder]').css('display', 'none');
                      //show only the one we need
                    $('[data-fbkholder="' + selected + '"]').css('display', 'inline');
                });
                this.el.tmpl('livedesk>providers/facebook', {}, function(){
                    self.el.off('keyup','.facebook-search-text').on('keyup','.facebook-search-text', function(e){
                        if(e.keyCode == 13 && $(this).val().length > 0) {
                            self.startSearch();
                        }
                    })
                });   
            },
            startSearch: function() {
                var self = this;
                var selected = self.el.find('#fbk-search-controls>li.active').attr('data-fbktab');
                var self = this;
                switch (selected) {
                    case 'post':
                        self.doPost();
                        break;
                    case 'comments':
                        self.doComments();
                        break;
                }
            },
            doComments: function(query) {
                var self = this,
                    el,
                    text = $('.facebook-search-text[data-fbkholder="comments"]').val();
                if (text.length < 1) {
                    return;
                }
                $('#fbk-comments-more').html('');
                query = typeof query !== 'undefined' ? query : '';
                if ( query == '') {
                    //new search
                    self.data.comments = [];
                    query = 'https://graph.facebook.com/comments/?limit=20&access_token=' + self.token + '&ids=' + encodeURIComponent(text) ;
                    $('#fbk-comments-results').html('');
                }
                query += '&callback=?'
                self.showLoading('#fbk-comments-more');
                $.jsonp({
                    url : query,
                }).fail(function(data){
                    self.stopLoading('#fbk-comments-more');
                    $.tmpl('livedesk>providers/no-results', {}, function(e,o) {
                        $('#fbk-comments-results').append(o);
                    });
                }).done(function(data){
                    //console.log(' de text ', data[text].comments);
                    var resTrue = false;
                    try {
                       if (data[text].comments.data.length > 0) {
                            resTrue = true;
                            data = data[text].comments;
                       }
                    }
                    catch (e) {
                       //console.log('error ', e);
                    }
                    try {
                        if ( data.data.length > 0 ) {
                            resTrue = true;
                        }
                    }
                    catch (e) {
                       //console.log('error ', e);
                    }

                    self.stopLoading('#fbk-comments-more');
                    if (resTrue/*data[text].comments.data.length > 0*/) {
                        //data = data[text].comments;
                        //prepare the data for dragging to timeline
                        results = new Array();
                        for ( var i = 0; i < data.data.length; i++ ) {
                            var item = data.data[i];
                            var it_arr = item.id.split('_');
                            item['story_id'] = it_arr[0];
                            item['fb_id'] = it_arr[1];
                            var time = new Date(item.created_time);
                            item['formated_time'] = time.format("dddd, mmmm dS, yyyy, h:MM:ss TT");
                            results.push(item);
                            item['permalink'] = text + '?fb_comment_id=fbc_' + item.id + '_' + item['story_id'];
                            self.data.comments[item.id] = item;
                        }
                        //display template
                        $.tmpl('livedesk>providers/facebook/item', 
                        {
                            results : data.data,
                        }, function(e,o) {
                            el = $('#fbk-comments-results').append(o).find('.facebook');
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
                                        $(this).data('data', self.adaptor.universal(self.data.comments[ itemNo ]));

                                    }
                                });
                            }).fail(function(){
                                el.removeClass('draggable').css('cursor','');
                            });
                        });
                        if (data.paging.next) {
                            $('#fbk-comments-more').tmpl('livedesk>providers/load-more', {name : 'fbk-comments-load-more'}, function(){
                                $(this).find('[name="fbk-comments-load-more"]').off('click').on('click', function(){
                                    self.doComments(data.paging.next)
                                });
                            });
                        } else {
                            $('#fbk-comments-more').html('');
                        }
                    } else {
                        //console.log('no more');
                        $.tmpl('livedesk>providers/no-results', {}, function(e,o) {
                            $('#fbk-comments-results').append(o);
                        });
                    }
                });
            },
            doPost : function(query) {
                var self = this,
                    el,
                    text = $('.facebook-search-text[data-fbkholder="post"]').val();
                if (text.length < 1) {
                    return;
                }
                $('#fbk-post-more').html('');
                query = typeof query !== 'undefined' ? query : '';
                if ( query == '') {
                    //new search
                    self.data.post = [];
                    //to search for posts we need to use v1.0 of the api(graph.facebook.com/v1.0/) with an api key of an app created earlier than 30.04.2014
                    query = 'https://graph.facebook.com/v1.0/search?type=post&access_token=' + self.token + '&limit=20&q=' + encodeURIComponent(text) ;
                    $('#fbk-post-results').html('');
                }
                query += '&callback=?'
                self.showLoading('#fbk-post-more');
                $.jsonp({
                    url : query,
                }).fail(function(data){
                    self.stopLoading('#fbk-post-more');
                    $.tmpl('livedesk>providers/no-results', {}, function(e,o) {
                        $('#fbk-post-results').append(o);
                    });
                }).done(function(data){
                    self.stopLoading('#fbk-post-more');
                    if (data.data.length > 0) {

                        //prepare the data for dragging to timeline
                        posts = [];
                        for ( var i = 0; i < data.data.length; i++ ) {
                            var item = data.data[i];
                            var it_arr = item.id.split('_');
                            item['story_id'] = it_arr[0];
                            item['fb_id'] = it_arr[1];
                            item['permalink'] = '//www.facebook.com/permalink.php?story_fbid=' + item['fb_id'] + '&id=' + item['story_id'];
                            var time = new Date(item.created_time);
                            item['formated_time'] = time.format("dddd, mmmm dS, yyyy, h:MM:ss TT");
                            posts.push({ Meta: item });
                            self.data.post[item.id] = item;
                        }
                        //console.log(posts)
                        $.tmpl('livedesk>items/item', { 
                            Post: posts,
                            Base: 'implementors/sources/facebook',
                            Item: 'sources/facebook'
                        }, function(e,o) {
                            //console.log(e,o)
                            el = $('#fbk-post-results').append(o).find('.facebook');
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
                                        $(this).data('data', self.adaptor.universal(self.data.post[ itemNo ]));
                                    }
                                });
                            }).fail(function(){
                                el.removeClass('draggable').css('cursor','');
                            });
                        });
                        if (data.paging) {
                            $('#fbk-post-more').tmpl('livedesk>providers/load-more', {name : 'fbk-post-load-more'}, function(){
                                $(this).find('[name="fbk-post-load-more"]').on('click', function(){
                                    self.doPost(data.paging.next)
                                });
                            });
                        } else {
                            $('#fbk-post-more').html('');
                        }
                    } else {
                        $.tmpl('livedesk>providers/no-results', {}, function(e,o) {
                            $('#fbk-post-results').append(o);
                        });
                    }
                });
            }
        });
    return providers;
});