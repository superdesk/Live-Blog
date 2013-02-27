/* 
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */

define('providers/flickr', [
    'providers',
    'jquery',
    config.guiJs('livedesk', 'action'),
    'jquery/jsonp',
    'jquery/tmpl',
    'jqueryui/draggable',
    'providers/flickr/adaptor',
    'tmpl!livedesk>providers/flickr',
    'tmpl!livedesk>providers/flickr/image-item',
    'tmpl!livedesk>providers/flickr/licenses',
    'tmpl!livedesk>providers/load-more',
    'tmpl!livedesk>providers/no-results',
    'tmpl!livedesk>providers/loading'
], function( providers,  $, BlogAction ) {
$.extend(providers.flickr, {
        initialized: false,
        per_page : 8,
	   apykey : 'd2a7c7c0a94ae40d01aee8238845bdba',
        url : 'http://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=%(apykey)s&text=%(text)s&format=json&nojsoncallback=1&per_page=%(per_page)s&page=%(start)s&license=%(license)s',
        licenseUrl : 'http://api.flickr.com/services/rest/?method=flickr.photos.licenses.getInfo&api_key=%(apykey)s&format=json&nojsoncallback=1',
        infoUrl : 'http://api.flickr.com/services/rest/?method=flickr.photos.getInfo&api_key=%(apykey)s&photo_id=%(id)s&secret=%(secret)s&format=json&nojsoncallback=1',
	data: [],
	init: function(){
                //console.log('flickr main init');
		if(!this.initialized || !this.el.children(":first").length) {
			this.render();
            this.adaptor.init();    
		}
		this.initialized = true;
	},
	render: function() {
		var self = this;
                
		this.el.tmpl('livedesk>providers/flickr', {}, function(){
			self.el.on('keyup','#flickr-search-text', function(e){
				if(e.keyCode == 13 && $(this).val().length > 0) {
					//enter press on google search text
					//check what search it is
					self.doFlickerImage(1);
				}
			})
                        .off('change', '#flickr-license')
                        .on('change', '#flickr-license', function(e){
                            self.doFlickerImage(1);
                        });
		});	  
                
                //get license options
                $.getJSON(str.format(this.licenseUrl,{apykey: this.apykey}), {}, function(data){
                        var licenses = {
                            licenses:data.licenses.license
                        }
                        $.tmpl('livedesk>providers/flickr/licenses', licenses, function(e,o) {
                            $('#flickr-license').append(o);
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
        doOriginalUrl : function(data) {
            for ( var i=0; i<data.photos.length; i++) {
                var item = data.photos[i];
                var fullUrl = str.format(this.infoUrl,{id: item.id, secret: item.secret, apykey: this.apykey});
                $.ajax({
                    url : fullUrl,
                    dataType: 'json',
                    success : function(data){
                        var url = data.photo.urls.url[0]
                        if (url.type == 'photopage') {
                            var id = data.photo.id;
                            $('[data-id="'+ id +'"]').attr('data-url',url._content);
                        }
                    },
                    error : function(){
                        //something went wrong
                    }
                })
            }
        },
        trimTitle: function(photos) {
            for( var i = 0; i < photos.length; i++ ) {
                photos[i].trimmedTitle = photos[i].title.trunc(80, true);
            }
            return photos;
        },
        doFlickerImage : function(start) {
            var self = this, el;
            var text = $('#flickr-search-text').val();
            if (text.length < 1) {
                return;
            }
            $('#flickr-image-more').html('');
            start = typeof start !== 'undefined' ? start : 1;
            if ( start == 1) {
                self.data = [];
                $('#flickr-image-results').html('');
            }
            
            var license = $('#flickr-license').val();
            
            
            var fullUrl = str.format(this.url,{start: start, text: text, apykey: this.apykey, license : license, per_page : this.per_page});
            this.showLoading('#flickr-image-more');
            $.getJSON(fullUrl, {}, function(data){
                    self.stopLoading('#flickr-image-more');
                    self.data = self.data.concat(data.photos.photo);
                    data.photos.photos = data.photos.photo;

                    if ( parseInt(data.photos.total) > 1 ) {
                        $.tmpl('livedesk>providers/flickr/image-item', 
                        {
                            photos : self.trimTitle(data.photos.photos),
                            page : parseInt(start - 1)
                        }, function(e,o) {
                            el = $('#flickr-image-results').append(o).find('.flickr');
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
                                        var idx = parseInt($(this).attr('idx'),10), page = parseInt($(this).attr('page'),10);
                                        var originalUrl = $(this).attr('data-url');
                                        var itemNo = parseInt( (page * self.per_page) + idx );
                                        self.data[itemNo].originalUrl = originalUrl;
                                        $(this).data('data', self.adaptor.universal(self.data[ itemNo ]));
                                    }
                                });
                            }).fail(function(){
                                el.removeClass('draggable');
                            });
                            self.doOriginalUrl(data.photos);
                        });			

                    //show the load more button
                        var cpage = parseInt(data.photos.page);
                        var totalpages = data.photos.pages;
                        var nextpage = parseInt(cpage + 1);
                        var loadMore = {
                            name : 'flickr-load-more'
                        }
                        
                        if ( nextpage <= totalpages ) {
                            $('#flickr-image-more').tmpl('livedesk>providers/load-more', loadMore, function(){
                                $(this).find('[name="flickr-load-more"]').on('click', function(){
                                    self.doFlickerImage(nextpage)
                                });
                            });
                        }
                        
                        
                    } else {
                        $.tmpl('livedesk>providers/no-results', {}, function(e,o) {
                            $('#flickr-image-results').append(o);
                        });
                        
                    }
                    
                    
            });

        },
        
});
return providers;
});