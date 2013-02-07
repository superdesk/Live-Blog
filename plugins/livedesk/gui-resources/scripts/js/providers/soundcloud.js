define('providers/soundcloud', [
    'providers',
    'providers/common',
    'jquery',
    config.guiJs('livedesk', 'action'),    
    'jquery/jsonp',
    'jquery/tmpl',
    'jqueryui/draggable',
    'providers/soundcloud/adaptor',
    'tmpl!livedesk>providers/soundcloud',
    'tmpl!livedesk>providers/soundcloud/sound-item',
    'tmpl!livedesk>providers/load-more',
    'tmpl!livedesk>providers/no-results',
    'tmpl!livedesk>providers/loading'
    ], function( providers, common, $, BlogAction) {
        $.extend(providers.soundcloud, common, {
            client_id : 'd913360f3cad924d67e1ad1887c00855',
            init : function() {
                if(!this.initialized || !this.el.children(":first").length) {
                    this.render();
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
                    //handle failure
                }).done(function(data){
                    self.stopLoading('#soundcloud-sound-more');
                    if (data.length > 0) {
                        //prepare the data for dragging to timeline
                        for (var i=0; i<data.length; i++) {
                            var item = data[i];
                            self.data[item.id] = item;
                            data[i].description = self.crudeTrim(data[i].description);
                        }
                        //display template
                        $.tmpl('livedesk>providers/soundcloud/sound-item', 
                        {
                            items : data,
                        }, function(e,o) {
                            el = $('#soundcloud-sound-results').append(o).find('.soundcloud');
                            BlogAction.get('modules.livedesk.blog-post-publish').done(function(action) {
                                el.draggable(
                                {
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
                                el.removeClass('draggable').css('cursor','');
                            });
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