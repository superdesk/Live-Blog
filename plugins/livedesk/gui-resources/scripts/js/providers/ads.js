define('providers/ads', 
[ 
  'providers', 'jquery', 'jquery/rest',
  'providers/ads/adaptor',
  'tmpl!livedesk>providers/ads',
  'tmpl!livedesk>providers/ads/items'
],
function(providers, $)
{
    $.extend(providers.ads,  
    {
        init: function(theBlog) 
        {
            this.adaptor.init();
            var self = this,
            getAds = function()
            {
                new $.restAuth(theBlog+'/PostType/advertisement/Post/Unpublished')
                .xfilter('CreatedOn,Content,PublishedOn,Type,Id,CId').done(function(data)
                {
                    $.tmpl('livedesk>providers/ads/items', {Posts: data}, function(e, o)
                    {  
                        $('.search-result-list', self.el).prepend(o);
                        $('.search-result-list li', self.el).draggable
                        ({
                            helper: 'clone',
                            appendTo: 'body',
                            zIndex: 2700,
                            start: function() 
                            {
                                $(this).data('data', self.adaptor.universal($(this)));
                            }
                        });
                    });
                });
            };
            $(self.el).tmpl('livedesk>providers/ads', getAds);
        }
    });
    return providers;
});