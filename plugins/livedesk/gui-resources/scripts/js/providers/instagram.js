define('providers/instagram', [
    'providers',
    'jquery',
    config.guiJs('livedesk', 'action'),
    'jquery/jsonp',
    'jquery/tmpl',
    'jqueryui/draggable',
    'providers/instagram/adaptor',
    config.guiJs('livedesk', 'providers-templates'),
    'tmpl!livedesk>items/item',
    'tmpl!livedesk>items/implementors/sources/base',
    'tmpl!livedesk>items/implementors/sources/instagram',
    'tmpl!livedesk>providers/instagram',
    'tmpl!livedesk>providers/instagram/image-item',
    'tmpl!livedesk>providers/load-more',
    'tmpl!livedesk>providers/no-results',
    'tmpl!livedesk>providers/loading'
    ], function( providers,  $, BlogAction ) {
       $.extend(providers.instagram, {
            cliend_id : '2bba61e66c8c4773b32c765955bd2b8d',
            url : 'https://api.instagram.com/v1/tags/%(apykey)s/media/recent?client_id=2bba61e66c8c4773b32c765955bd2b8d', 
            init : function() {
                if(!this.initialized || !this.el.children(":first").length) {
                    this.adaptor._parent = this;
                    this.adaptor.init();
                }
                this.data = {};
                this.initialized = true;
            }, 
            render: function() {
                var self = this;
                this.el.tmpl('livedesk>providers/instagram', {}, function(){
                    self.el.on('keyup','#instagram-search-text', function(e){
                        if(e.keyCode == 13 && $(this).val().length > 0) {
                            self.doInstagramImage();
                        }
                    })
                });   
            },
            showLoading : function(where) {
                $(where).tmpl('livedesk>providers/loading', function(){
                });
            },
            stopLoading : function(where) {
                $(where).html('');
            },
            doInstagramImage : function(query) {
                var self = this, el;
                var text = $('#instagram-search-text').val();
                text = text.replace(' ', '')
                if (text.length < 1) {
                    return;
                }
                $('#instagram-image-more').html('');
                query = typeof query !== 'undefined' ? query : '';
                if ( query == '') {
                    self.data = [];
                    $('#instagram-image-results').html('');
                    query = 'https://api.instagram.com/v1/tags/' + encodeURIComponent(text) + '/media/recent?client_id=2bba61e66c8c4773b32c765955bd2b8d&callback=?';
                } 
                self.showLoading('#instagram-image-more');
                $.jsonp({
                    url : query,
                }).fail(function(data){
                    self.stopLoading('#instagram-image-more');
                    //handle failure
                }).done(function(data){
                    self.stopLoading('#instagram-image-more');
                    for( var posts = [], i = 0, item=data.data[i], count = data.data.length; i < count; item = data.data[++i] ){
						posts.push({ Meta: item});
                        self.data[item.id] = item;
                    }
                    if (posts.length > 0) {
                         $.tmpl('livedesk>items/item', { 
                                Post: posts,
                                Base: 'implementors/sources/instagram',
                                Item: 'sources/instagram'
                            }, function(e,o) {
                                el = $('#instagram-image-results').append(o).find('.instagram'); 
                                BlogAction.get('modules.livedesk.blog-post-publish').done(function(action) {
                                    el.draggable({
                                        addClasses: false,
                                        revert: 'invalid',
                                        containment:'document',
                                        helper: 'clone',
                                        appendTo: 'body',
                                        zIndex: 2700,
                                        clone: true,
                                        start: function(evt, ui) {
                                            item = $(evt.currentTarget);
                                            $(ui.helper).css('width', item.width());
                                            var itemNo = $(this).attr('data-id');
                                            $(this).data('data', self.adaptor.universal(self.data[ itemNo ]));
                                        }
                                    });
                                }).fail(function(){
                                    el.removeClass('draggable');
                                });
                            });
                        var loadMore = {
                            name : 'instagram-load-more'
                        }
                        if ( typeof data.pagination.next_url != 'undefined') {
                            $('#instagram-image-more').tmpl('livedesk>providers/load-more', loadMore, function(){
                                $(this).find('[name="instagram-load-more"]').on('click', function(){
                                    self.doInstagramImage(data.pagination.next_url)
                                });
                            });
                        }
                    } else {
                        $.tmpl('livedesk>providers/no-results', {}, function(e,o) {
                            $('#instagram-image-results').append(o);
                        });
                    }
                });
            }
        });
    return providers;
});