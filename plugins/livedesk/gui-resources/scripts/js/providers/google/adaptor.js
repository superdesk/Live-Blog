define('providers/google/adaptor', [
    'providers',
    'utils/str',
    'jquery',
    'gizmo',
    'jquery/rest',
    'jquery/utils',
    'providers/google/tab',
    'tmpl!livedesk>providers/google/post'
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
                //self.data.Content = $('.google-full-content .result-text', self.el).html();
                self.data.Meta.annotation = [$('.google-full-content .annotation:eq(0)', self.el).html(), 
                    $('.google-full-content .annotation:eq(1)', self.el).html()];
                self.data.Meta = JSON.stringify(self.data.Meta);
                
                self.parent.insert(self.data, self);
                
                $('.actions', self.el).addClass('hide');
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
            $.tmpl('livedesk>providers/google/post', this.data, function(e, o)
            { 
                self.el.addClass( $(o).attr('class') );
                self.el.html( $(o).html() );
                $('.actions', self.el).removeClass('hide');
            });
        }
    });
    
    $.extend(providers.google, 
    {
        adaptor: 
        {
            author: 1,
            init: function() 
            {
                var self = this;
                new $.rest('Data/Collaborator/')
                    .xfilter('Id')
                    .request({data: { 'qs.name': 'google'}})
                    .done(function(collabs)
                    {
                        if($.isDefined(collabs[0])) 
                            self.author = collabs[0].Id;
                    });
            },
            universal: function(obj) 
            {
                var meta =  jQuery.extend(true, {}, obj);
                delete meta.content;
                return new AnnotateView
                ({
                    data: 
                    {
                        Content: obj.content,
                        Type: 'normal',
                        Author: this.author,
                        Meta: meta
                    }
                });
            },
            
			// Todo remove this stuff
            web: function(obj) {
                delete obj['$idx'];
				delete obj['$len'];
				delete obj['GsearchResultClass'];
				return {
                    Content: str.format('<h3><a href="%(url)s">%(title)s</a></h3><p class="result-text">%(content)s</p><i class="source-icon"><img src="http://g.etfv.co/%(url)s" style="max-width: 16px" border="0"></i><a class="author-name" href="%(url)s">%(visibleUrl)s</a>',obj),
                    Type: 'normal',
                    Author: this.author,
					Meta: obj
                };
            },
            news: function(obj) {
                return {
                    Content: str.format('<h3><a href="%(url)s">%(title)s</a></h3><p class="result-text">%(content)s</p><i class="source-icon"><img src="http://g.etfv.co/%(url)s" style="max-width: 16px" border="0"></i><a class="author-name" href="%(unescapedUrl)s">%(publisher)s</a>',obj),
                    Type: 'normal',
                    Author: this.author,
					Meta: obj
                };
            },
            images: function(obj) {
                return {
                    Content: str.format('<p class="result-text">%(content)s</p><a href="%(url)s"><img src="%(tbUrl)s"/></a>', obj),
                    Type: 'normal',
                    Author: this.author,
					Meta: obj
                };
            }
        }
    });
	return providers;
});