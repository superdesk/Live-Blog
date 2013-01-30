define('providers/youtube/adaptor', 
[
    'providers',
    'utils/str',
    'jquery',
    'gizmo',
    'jquery/rest',
    'jquery/utils',
    'providers/youtube/tab',
    'tmpl!livedesk>providers/youtube/post'
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
                self.data.Content = $('.youtube-full-content .result-text', self.el).html();
                
                self.data.Meta.annotation = [$('.youtube-full-content .annotation:eq(0)', self.el).html(), 
                    $('.youtube-full-content .annotation:eq(1)', self.el).html()];
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
            this.el.tmpl('livedesk>providers/youtube/post', this.data);
            this.el.addClass('with-avatar youtube clearfix');
            $('.actions', this.el).removeClass('hide');
        }
    });
    
    $.extend(providers.youtube, 
    {
        adaptor: 
        {
            author: 1,
            init: function() 
            {
                var self = this;
                new $.rest('Data/Collaborator/')
                    .xfilter('Id')
                    .request({data: { 'qs.name': 'youtube'}})
                    .done(function(collabs)
                    {
                        if($.isDefined(collabs[0])) 
                            self.author = collabs[0].Id;
                    });
            },
            universal: function(obj) 
            {
                var meta =  jQuery.extend(true, {}, obj);
                var returner = new AnnotateView
                ({
                    data: 
                    {
                        Content: obj.title,
                        Type: 'normal',
                        Author: this.author,
                        Meta: meta
                    }
                });
                return returner;
            }
        }
    });
	return providers;
});

