define('providers/instagram/adaptor', 
[
    'providers',
    'utils/str',
    'jquery',
    'gizmo',
    'jquery/rest',
    'jquery/utils',
    'providers/instagram/tab',
    'tmpl!livedesk>providers/instagram/post'
], 
function(providers,str, $, Gizmo)
{
    var AnnotateView = Gizmo.View.extend
    ({
        tagName: 'li',
        init: function(data)
        {
            var self = this;
            $(self.el).on('click', '.btn.publish', function()
            {
                self.data.Content = $('.instagram-full-content .result-text', self.el).html();
                self.data.Meta.annotation = $('.instagram-full-content .annotation:eq(0)', self.el).html();
                self.data.Meta = JSON.stringify(self.data.Meta);
                self.parent.insert(self.data, self);
                $('.actions', self.el).remove();
            })
			.on('click', '.btn.cancel', function()
            {
                self.parent = null;
                self.el.remove();
            })
			.on('click', 'a.close', function(){
				$('#delete-post .yes')
					.off(self.getEvent('click'))
					.on(self.getEvent('click'), function(){
						self.parent = null;
						self.el.remove();
					});				
			});
			
        },
        render: function()
        {
            if ( typeof this.data.Meta.annotation == 'undefined' ) {
                this.data.Meta.annotation = "<br />";
            }
            this.el.tmpl('livedesk>providers/instagram/post', this.data);
            this.el.addClass('with-avatar instagram clearfix');
            $('.actions', this.el).removeClass('hide');
        }
    });
    
    $.extend(providers.instagram, 
    {
        adaptor: 
        {
            author: 1,
            init: function() 
            {
                var self = this;
                new $.rest('Data/Collaborator/')
                    .xfilter('Id, Source.Key')
                    .request({data: { 'qs.name': 'instagram'}})
                    .done(function(collabs)
                    {
                        if($.isDefined(collabs[0])){
                            self.author = collabs[0].Id;
                            self.key = collabs[0].Source.Key;
                        }
                        self._parent.client_id = self.key;
                        self._parent.render(); 
                    });
            },
            universal: function(obj) 
            {
                var meta =  jQuery.extend(true, {}, obj);                
                return new AnnotateView
                ({
                    data: 
                    {
                        Creator: localStorage.getItem('superdesk.login.id'),
                        Content: obj.images.standard_resolution.url,
                        Type: 'normal',
                        Author: this.author,
                        Meta: meta
                    }
                });
            },
        }
    });
	return providers;
});

