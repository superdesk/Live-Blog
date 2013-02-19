define('providers/twitter/adaptor', [
    'providers',
    'utils/str',
    'jquery',
    'gizmo/superdesk',
    'jquery/superdesk',
    'jquery/rest',
    'jquery/utils',
    'providers/twitter/tab',
    'tmpl!livedesk>providers/twitter/post'
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
                //self.data.Content = $('.twitter-full-content .result-text', self.el).html();
                self.data.Meta.annotation = [$('.twitter-full-content .annotation:eq(0)', self.el).html(), $('.twitter-full-content .annotation:eq(1)', self.el).html()];
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
            var self = this;
            
            if ( typeof this.data.Meta.annotation == 'undefined' ) {
                this.data.Meta.annotation = {before: "<br />", after: "<br />"};
            }
            $.tmpl('livedesk>providers/twitter/post', this.data, function(e, o)
            { 
                self.el.addClass( $(o).attr('class') );
                self.el.html( $(o).html() );
                $('.actions', self.el).removeClass('hide');
            });
        }
    });
    
    $.extend(providers.twitter, 
    {
        adaptor: 
        {
            author: 1,
            init: function() 
            {
                var self = this;
                    Colabs = Gizmo.Collection.extend({  url: new Gizmo.Url('Data/Collaborator/') }),
                    colabs = new Colabs;
                colabs.xfilter('Id')
                    .sync({data: { 'qs.name': 'twitter'}})
                    .done(function()
                    {
                        colabs.each(function(){ self.author = this.get('Id'); return false; });
                    });
            },
            universal: function(obj) 
            {
                var meta =  jQuery.extend(true, {}, obj);
                delete meta.text
                
                return new AnnotateView
                ({
                    data: 
                    {
                        Creator: localStorage.getItem('superdesk.login.id'),
                        Content: obj.text,
                        Type: 'normal',
                        Author: this.author,
                        Meta: meta
                    }
                });
            }
        }
    });
    return providers;
});


