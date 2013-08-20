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
    'use strict';

    function trimTo(content, amount) {
        if (typeof content == 'undefined') {
            content = '';
        }

        if (content.length > amount) {
            return content.substr(0, amount) + ' ...';
        } else {
            return content;
        }
    }

    var GoogleProvider = function(type) {
        var URL = 'https://ajax.googleapis.com/ajax/services/search/%(type)s?v=1.0&start=%(start)s&q=%(text)s&callback=?';
        var provider = this;

        provider.type = type;
        provider.data = [];

        this.getURL = function(query, start) {
            return str.format(URL, {type: provider.type, start: start, text: query});
        };

        this.getData = function(idx) {
            return provider.data[idx];
        };

        /**
         * Search provider
         *
         * @param {string} query
         * @param {int} start
         * @return {object} promise
         */
        this.search = function(query, start) {
            start = parseInt(start) || 0;
            if (start === 0) {
                provider.data = [];
            }

            var delay = $.Deferred();
            $.getJSON(this.getURL(query, start),
                function(response) {
                    var posts = [];
                    for (var i = 0; i < response.responseData.results.length; i++) {
                        response.responseData.results[i].type = type;
                        response.responseData.results[i].trimContent = trimTo(response.responseData.results[i].content, 200);
                        posts.push({Meta: response.responseData.results[i]});
                    }

                    provider.data.push.apply(provider.data, response.responseData.results);
                    delay.resolve(
                        posts,
                        parseInt(response.responseData.cursor.currentPageIndex),
                        response.responseData.cursor.pages
                    );
                });
            return delay.promise();
        };
    };

    $.extend(providers.google, {
        initialized: false,
        providers: {},

        init: function(){
            if (!this.initialized) {
                this.initialized = true;
                this.adaptor.init();

                this.providers.web = new GoogleProvider('web');
                this.providers.news = new GoogleProvider('news');
                this.providers.images = new GoogleProvider('images');
            }

            this.render();
        },

        getProvider: function(type) {
            return this.providers[type];
        },

        render: function() {
            var self = this;
            this.el.tmpl('livedesk>providers/google', {}, function(){
                $(self.el)
                    .off('click.livedesk')
                    .on('click.livedesk', '#ggl-search-controls>li', function(evt) {
                        evt.preventDefault();
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
            fresh =  !! fresh;

            if ($('#ggl-web-tab').hasClass('active')) {
               //do google search
               if (fresh || $('#ggl-web-results').html() == '') {
                   this.doSearch('web');
               }
            }

            if ( $('#ggl-news-tab').hasClass('active') ) {
                //do google search
                if (fresh || $('#ggl-news-results').html() == '') {
                    this.doSearch('news');
                }
            }

            if ( $('#ggl-images-tab').hasClass('active') ) {
                //do google search
                if (fresh || $('#ggl-images-results').html() == '') {
                    this.doSearch('images');
                }
            }
        },
        
        showLoading: function(el) {
            el.tmpl('livedesk>providers/loading');
        },

        stopLoading : function(el) {
            el.html('');
        },

        doSearch: function(type, start) {
            var self = this;
            var showMore = $('#ggl-' + type + '-holder').find('.sources-show-more');
            var text = $('#google-search-text').val();
            if (text.length < 1) {
                return;
            }

            showMore.html('');
            start = parseInt(start, 10) || 0;
            if (start === 0) {
                $('#ggl-' + type + '-results').html('');
            }

            var currentDate = new Date();
            this.showLoading(showMore);

            var provider = this.getProvider(type);
            provider.search(text, start).
                then(function(posts, cpage, pages) {
                    self.stopLoading(showMore);
                    //data.responseData.date = currentDate;
                    if (posts.length > 0 ) {
                         $.tmpl('livedesk>items/item', {
                                Post: posts,
                                Base: 'implementors/sources/google',
                                Item: 'sources/google/' + type,
                                startx: start,
                            }, function(e,o) {
                                var getData = function(item) {
                                    var idx = parseInt(item.attr('idx'), 10);
                                    var startx = parseInt(item.attr('startx'), 10);
                                    return provider.getData(startx + idx);
                                };

                                var el = $('#ggl-' + type + '-results').append(o).find('.google');
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
                                            var item = $(evt.currentTarget);
                                            $(ui.helper).css('width', item.width());
                                            $(this).data('data', self.adaptor.universal(getData(item)));
                                        }
                                    });

                                    $('.saveonly button', self.el).click(function(e) {
                                        if ($(e.target).attr('disabled')) {
                                            return;
                                        }

                                        var item = $(e.target).closest('li');
                                        var model = self.adaptor.parse(getData(item));
                                        model.Meta = JSON.stringify(model.Meta);
                                        $.post(self.theBlog + '/Post', model, function(data, textStatus) {
                                            item.find('.saveonly button').attr('disabled', 'disabled');
                                        }, 'json');
                                    });
                                }).fail(function(){
                                    el.removeClass('draggable');
                                });
                        });

                        cpage += 1;
                        for (var i = 0; i < pages.length; i++) {
                            var page = pages[i];
                            if (cpage < page.label) {
                                //show load more results
                                showMore.tmpl('livedesk>providers/google-more', function() {
                                    $(this).find('[name="more_results"]').on('click', function() {
                                        self.doSearch(type, page.start);
                                    });
                                });
                                break;
                            }
                        }
                    } else {
                        //no results
                        $.tmpl('livedesk>providers/no-results', data.responseData, function(e,o) {
                            $('#ggl-' + type + '-results').append(o);
                        });
                    }
                });
        }
    });

    return providers;
});