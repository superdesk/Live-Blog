define('providers/instagram', [
    'providers',
    'jquery',
    config.guiJs('livedesk', 'action'),
    'jquery/jsonp',
    'jquery/tmpl',
    'jqueryui/draggable',
    'providers/instagram/adaptor',
    'tmpl!livedesk>providers/instagram',
    'tmpl!livedesk>providers/instagram/image-item',
    'tmpl!livedesk>providers/load-more',
    'tmpl!livedesk>providers/no-results',
    'tmpl!livedesk>providers/generic-error',
    'tmpl!livedesk>providers/loading'
    ], function( providers,  $, BlogAction ) {
       $.extend(providers.instagram, {
            cliend_id : '0',
            init : function() {
                if(!this.initialized || !this.el.children(":first").length) {
                    this.adaptor._parent = this;
                    this.adaptor.init();
                }
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
            showError: function(message) {
                if (typeof message == 'undefined') {
                    message = '';
                }
                $.tmpl('livedesk>providers/generic-error', {message: message}, function(e,o) {
                    $('#instagram-image-results').append(o);
                });
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
                    query = 'https://api.instagram.com/v1/tags/' + encodeURIComponent(text) + '/media/recent?client_id=' + encodeURIComponent(self.client_id) + '&callback=?';
                } 
                self.showLoading('#instagram-image-more');
                $.jsonp({
                    url : query,
                }).fail(function(data){
                    self.stopLoading('#instagram-image-more');
                }).done(function(data){

                    self.stopLoading('#instagram-image-more');

                    if ( data.meta.code == 400 ) {
                        self.showError(_('Invalid API Key (Key has invalid format)'));
                        return;
                    }

                    var images = data.data;

                    if (images.length > 0) {

                        for (var i=0; i<images.length; i++) {
                            var image = images[i];
                            self.data[image.id] = image;
                        }

                        $.tmpl('livedesk>providers/instagram/image-item', 
                        {
                            photos : images,
                        }, function(e,o) {
                            el = $('#instagram-image-results').append(o).find('.instagram');              
                            BlogAction.get('modules.livedesk.blog-post-publish').done(function(action) {
                                el.draggable({
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