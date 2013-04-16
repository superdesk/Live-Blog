/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

define('providers/google', [
	'providers',
    'utils/str', 
	'jquery',
    config.guiJs('livedesk', 'action'),
    'jquery/tmpl',
	'jqueryui/draggable',
    'providers/google/adaptor',
    config.guiJs('livedesk', 'providers-templates'),
    'tmpl!livedesk>items/item',
    'tmpl!livedesk>items/implementors/sources/base',
    'tmpl!livedesk>items/implementors/sources/google',
	'tmpl!livedesk>providers/google',
	'tmpl!livedesk>providers/google-more',
    'tmpl!livedesk>providers/no-results',
    'tmpl!livedesk>providers/loading'
], function( providers, str, $, BlogAction ) {
$.extend(providers.google, {
	initialized: false,
	url: 'https://ajax.googleapis.com/ajax/services/search/%(type)s?v=1.0&start=%(start)s&q=%(text)s&callback=?',
	urls: {
		web: '',
		news: '',
		images: ''
	},
	data: [],
	init: function(){
//		if(!this.initialized) {
			this.urls.web = str.format(this.url,{type:'web'});
			this.urls.news = str.format(this.url,{type:'news'});
			this.urls.images = str.format(this.url,{type:'images'});
			this.adaptor.init();
            this.render();
//		}
		this.initialized = true;
	},
	render: function() {
		var self = this;
		this.el.tmpl('livedesk>providers/google', {}, function(){
			$(self.el)
            .off('click.livedesk')
            .on('click.livedesk', '#ggl-search-controls>li', function(ev){
			  $(this).siblings().removeClass('active') .end()
					 .addClass('active');			  
			  var myArr = $(this).attr('id').split('-');
			  
			  //hide all ggl result holders
			  self.el.find('.scroller').css('visibility', 'hidden');
			  //show only the one we need
			  $('#ggl-'+myArr[1]+'-holder').css('visibility', 'visible');
			  self.startSearch(false);
			})
            .off('keyup.livedesk')
			.on('keyup.livedesk','#google-search-text', function(e){
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
       if ( $('#ggl-web-tab').hasClass('active') ) {
               //do google search
               if (fresh || $('#ggl-web-results').html() == '') {
                   self.doWeb();
               }
           }
           
           if ( $('#ggl-news-tab').hasClass('active') ) {
               //do google search
               if (fresh || $('#ggl-news-results').html() == '') {
				   self.doNews();
               }
           }
           
           if ( $('#ggl-images-tab').hasClass('active') ) {
               //do google search
               if (fresh || $('#ggl-images-results').html() == '') {
				   self.doImages();
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
	doWeb: function (start) {
                var self = this, el, posts = [];
                var text = $('#google-search-text').val();
                if (text.length < 1) {
                    return;
                }
                $('#ggl-web-more').html('');
                start = typeof start !== 'undefined' ? start : 0;
                if ( start == 0) {
                    self.data.web = [];
                    $('#ggl-web-results').html('');
                }
                var currentDate = new Date(), currentStr = currentDate.toLocaleDateString();// + ' ' + currentDate.toLocaleTimeString();
                this.showLoading('#ggl-web-more');
                $.getJSON(str.format(this.urls.web,{
                    start: start,
                    text: text
                }), {}, function(data){
                    self.stopLoading('#ggl-web-more');
                    self.data.web = self.data.web.concat(data.responseData.results);
                    data.responseData.date = currentDate;
                    if ( data.responseData.results.length > 0 ) {
                        for( var i = 0, count = data.responseData.results.length; i < count; i++ ){
                            data.responseData.results[i].type = 'web';
                            posts.push({ Meta: data.responseData.results[i]});
                        }
                         $.tmpl('livedesk>items/item', { 
                                Post: posts,
                                Base: 'implementors/sources/google',
                                Item: 'sources/google/web',
                                startx: start,
                            }, function(e,o) {
                                el = $('#ggl-web-results').append(o).find('.google');
                                BlogAction.get('modules.livedesk.blog-post-publish').done(function(action) {
									el.draggable({
                                        scroll: true,
										//snap: true,
										//containment: 'document',
										addClasses: false,
                                        revert: 'invalid',
                                        helper: 'clone',
                                        appendTo: 'body',
                                        zIndex: 2700,
                                        clone: true,
                                        start: function(evt, ui) {
                                            item = $(evt.currentTarget);
                                            $(ui.helper).css('width', item.width());
                                            var idx = parseInt($(this).attr('idx'),10), startx = parseInt($(this).attr('startx'),10);
                                            $(this).data('data', self.adaptor.universal(self.data.web[startx+idx]));
                                        }

                                    });
                                }).fail(function(){
                                    el.removeClass('draggable');
                                });
                        });
                        var cpage = parseInt(data.responseData.cursor.currentPageIndex);
                        cpage += 1;

                        var pages = data.responseData.cursor.pages;

                        for(var i=0; i< pages.length; i++) {
                            var page = pages[i];
                            if (cpage < page.label) {
                                //show load more results
                                $('#ggl-web-more').tmpl('livedesk>providers/google-more', function(){
                                    $(this).find('[name="more_results"]').on('click', function(){
                                        self.doWeb(page.start)
                                    });
                                });
                                break;
                            }
                        }
                    } else {
                        //no results
                        $.tmpl('livedesk>providers/no-results', data.responseData, function(e,o) {
                            $('#ggl-web-results').append(o);
                        });
                    }
                });
            },
        trimTo : function(content, amount) {
            if (typeof content == 'undefined') {
                content = '';
            }
            if ( typeof amount != 'number' ) {
                amount = 200;
            }
            if ( content.length > 200) {
                return content.substr(0, amount) + ' ...'
            } else {
                return content;
            }
        },
	doNews: function (start) {
                var self = this, el, posts = [];
                var text = $('#google-search-text').val();		
                if (text.length < 1) {
                    return;
                }		
                $('#ggl-news-more').html('');
                start = typeof start !== 'undefined' ? start : 0;
                if ( start == 0) {
                    self.data.news = [];
                    $('#ggl-news-results').html('');
                }
                var currentDate = new Date(), currentStr = currentDate.toLocaleDateString();// + ' ' + currentDate.toLocaleTimeString();
                this.showLoading('#ggl-news-more');
                $.getJSON(str.format(this.urls.news,{
                    start: start, 
                    text: text
                }), {}, function(data){
                    self.stopLoading('#ggl-news-more');
                    self.data.news = self.data.news.concat(data.responseData.results);
                    data.responseData.date = currentDate;
                    if ( data.responseData.results.length > 0 ) {
                        for( var item, i = 0, count = data.responseData.results.length; i < count; i++ ){
                            item = data.responseData.results[i];
                            item.type = 'news';
                            item.trimContent = self.trimTo(item.content, 200);
                            posts.push({ Meta: item});
                        }
                        $.tmpl('livedesk>items/item', { 
                                Post: posts,
                                Base: 'implementors/sources/google',
                                Item: 'sources/google/news',
                                startx: start,
                            }, function(e,o) {
                                el = $('#ggl-news-results').append(o).find('.google');
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
                                            var idx = parseInt($(this).attr('idx'),10), startx = parseInt($(this).attr('startx'),10);
                                            $(this).data('data', self.adaptor.universal(self.data.news[startx+idx]));
                                        }

                                    });
                                }).fail(function(){
                                    el.removeClass('draggable');
                                });
                        });
                        var cpage = parseInt(data.responseData.cursor.currentPageIndex);
                        cpage += 1;

                        var pages = data.responseData.cursor.pages;

                        for(var i=0; i< pages.length; i++) {
                            var page = pages[i];
                            if (cpage < page.label) {
                                //show load more results
                                $('#ggl-news-more').tmpl('livedesk>providers/google-more', function(){
                                    $(this).find('[name="more_results"]').on('click', function(){
                                        self.doNews(page.start)
                                    });
                                });
                                break;
                            }
                        }
                    } else {
                        //no results
                        $.tmpl('livedesk>providers/no-results', data.responseData, function(e,o) {
                            $('#ggl-news-results').append(o);
                        });
                    }
                    
			
                });
            },
	doImages: function (start) {
                var self = this, el, posts = [];
                var text = $('#google-search-text').val();		
                if (text.length < 1) {
                    return;
                }		
                $('#ggl-images-more').html('');
                start = typeof start !== 'undefined' ? start : 0;
                if ( start == 0) {
                    self.data.images = [];
                    $('#ggl-images-results').html('');
                }
                var currentDate = new Date(), currentStr = currentDate.toLocaleDateString();// + ' ' + currentDate.toLocaleTimeString();
                this.showLoading('#ggl-images-more');
                $.getJSON(str.format(this.urls.images,{
                    start: start, 
                    text: text
                }), {}, function(data){
                    self.stopLoading('#ggl-images-more');
                    self.data.images = self.data.images.concat(data.responseData.results);
                    data.responseData.date = currentDate;
                    if ( data.responseData.results.length > 0 ) {
                        for( var i = 0, count = data.responseData.results.length; i < count; i++ ){
                            data.responseData.results[i].type = 'images';
                            posts.push({ Meta: data.responseData.results[i]});
                        }
                        console.log(posts);
                         $.tmpl('livedesk>items/item', { 
                                Post: posts,
                                Base: 'implementors/sources/google',
                                Item: 'sources/google/images',
                                startx: start,
                            }, function(e,o) {
                                el = $('#ggl-images-results').append(o).find('.google');
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
                                            var idx = parseInt($(this).attr('idx'),10), startx = parseInt($(this).attr('startx'),10);
                                            $(this).data('data', self.adaptor.universal(self.data.images[startx+idx]));
                                        }

                                    });
                                }).fail(function(){
                                    el.removeClass('draggable');
                                });
                        });			
                        var cpage = parseInt(data.responseData.cursor.currentPageIndex);
                        cpage += 1;

                        var pages = data.responseData.cursor.pages;

                        for(var i=0; i< pages.length; i++) {
                            var page = pages[i];
                            if (cpage < page.label) {
                                //show load more results
                                $('#ggl-images-more').tmpl('livedesk>providers/google-more', function(){
                                    $(this).find('[name="more_results"]').on('click', function(){
                                        self.doImages(page.start)
                                    });
                                });
                                break;
                            }
                        }
                    } else {
                        $.tmpl('livedesk>providers/no-results', data.responseData, function(e,o) {
                            $('#ggl-images-results').append(o);
                        });
                    }
                    
			
                });
            }		
});


return providers;
});