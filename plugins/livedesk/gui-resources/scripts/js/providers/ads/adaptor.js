define('providers/ads/adaptor', [
    'providers',
    'utils/str',
    'jquery',
    'gizmo',
    'jquery/rest',
    'jquery/utils',
    'providers/ads/tab',
    'tmpl!livedesk>providers/ads/post'
], function(providers,str, $, Gizmo)
{
    var AnnotateView = Gizmo.View.extend
    ({
        tagName: 'li',
        init: function(data)
        {
            var self = this;
            $(self.el).on('click', '.btn.publish', function()
            {
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
            var self = this;
            $.tmpl('livedesk>providers/ads/post', this.data, function(e, o)
            { 
                self.el.addClass( $(o).attr('class') );
                self.el.html( $(o).html() );
                $('.actions', self.el).removeClass('hide');
            });
        }
    });
    
    $.extend(providers.ads, 
    {
        adaptor: {
            author: 1,
            init: function() {
                var self = this;
                new $.rest('Data/Collaborator/')
                    .xfilter('Id')
                    .request({data: { 'qs.name': 'advertisement'}})
                    .done(function(collabs)
                    {
                        if($.isDefined(collabs[0])) {
                            self.author = collabs[0].Id;
                        }
                    });
            },
            universal: function(obj)
            {                 
                return new AnnotateView
                ({
                    data: 
                    {
                        Content: $(obj).html(),
                        Type: 'advertisement',
                        Author: this.author
                    }
                });
            }
        }
    });
    return providers;
});


