define('providers/soundcloud', [
    'providers',
    'providers/common',
    'jquery',
    config.guiJs('livedesk', 'action'),    
    'jquery/jsonp',
    'jquery/tmpl',
    'jqueryui/draggable',
    'providers/soundcloud/adaptor',
    config.guiJs('livedesk', 'providers-templates'),
    'tmpl!livedesk>items/item',
    'tmpl!livedesk>items/implementors/sources/base',
    'tmpl!livedesk>items/implementors/sources/soundcloud',
    'tmpl!livedesk>providers/soundcloud',
    'tmpl!livedesk>providers/soundcloud/sound-item',
    'tmpl!livedesk>providers/load-more',
    'tmpl!livedesk>providers/no-results',
    'tmpl!livedesk>providers/api-key-error',
    'tmpl!livedesk>providers/loading'
    ], function( providers, common, $, BlogAction) {
        $.extend(providers.soundcloud, common, {
            client_id : 'd913360f3cad924d67e1ad1887c00855',
            init : function() {
                if(!this.initialized || !this.el.children(":first").length) {
                    this.adaptor._parent = this;
					this.adaptor.init();
                }
                this.initialized = true;
            }, 
            render: function() {
                var self = this;
                this.el.tmpl('livedesk>providers/soundcloud', {}, function(){
                    self.el.on('keyup','#soundcloud-search-text', function(e){
                        if(e.keyCode == 13 && $(this).val().length > 0) {
                            self.doSoundcloud();
                        }
                    })
                });   
            },
            doSoundcloud : function(query) {
                var self = this,
                    el,
                    text = $('#soundcloud-search-text').val();
                if (text.length < 1) {
                    return;
                }
                $('#soundcloud-sound-more').html('');
                query = typeof query !== 'undefined' ? query : '';
                if ( query == '') {
                    self.data = [];
                    $('#soundcloud-sound-results').html('');
                    query = 'https://api.soundcloud.com/tracks.json?client_id=' + self.client_id + '&q=' + encodeURIComponent(text) + '&callback=?';
                } 
                self.showLoading('#soundcloud-sound-more');
                $.jsonp({
                    url : query,
                }).fail(function(data){
                    self.stopLoading('#soundcloud-sound-more');
                    $.tmpl('livedesk>providers/api-key-error', {}, function(e,o) {
                        $('#soundcloud-sound-results').append(o);
                    });
                }).done(function(data){
                    self.stopLoading('#soundcloud-sound-more');
                    if (data.length > 0) {
                        //prepare the data for dragging to timeline
                        for( var created, posts = [], i = 0, count = data.length; i < count; i++ ){
                            var item = data[i];
                            created = new Date(item.created_at);
                            item.created_at_iso = created.toISOString();
                            item.iframe = 'http://w.soundcloud.com/player/?url=http%3A%2F%2Fapi.soundcloud.com%2Ftracks%2F'+item.id+'&show_artwork=true';
                            self.data[item.id] = item;
                            posts.push({ Meta: item });
                        }
                        $.tmpl('livedesk>items/item', { 
                                Post: posts,
                                Base: 'implementors/sources/soundcloud',
                                Item: 'sources/soundcloud'
                            }, function(e,o) {
                                el = $('#soundcloud-sound-results').append(o).find('.soundcloud'); 
                                BlogAction.get('modules.livedesk.blog-post-publish').done(function(action) {
                                    el.draggable({
                                        addClasses: false,
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
                                            $(this).data('data', self.adaptor.universal(self.data[ itemNo ]));
                                        }
                                    });
                                }).fail(function(){
                                    el.removeClass('draggable');
                                });
                                /*!
                                 * Request aditional information for the image, not used for now
                                 */
                                //self.doOriginalUrl(data.photos);
                            });
                    } else {
                        $.tmpl('livedesk>providers/no-results', {}, function(e,o) {
                            $('#soundcloud-sound-results').append(o);
                        });
                    }
                });
            }
        });
    return providers;
});