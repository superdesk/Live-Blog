define('providers/ads/adaptor', [
    'providers', 'jquery', 'providers/ads/tab'
], function(providers, $)
{
    $.extend(providers.ads, 
    {
        adaptor: {
            author: 1,
            init: function() {
                var self = this;
                new $.rest('Superdesk/Collaborator/')
                    .xfilter('Id')
                    .request({data: { name: 'advertisement'}})
                    .done(function(collabs)
                    {
                        if($.isDefined(collabs[0])) {
                            self.author = collabs[0].Id;
                        }
                    });
            },
            universal: function(obj)
            {
                return {
                    Content: $(obj).find('.result-text').html(),
                    Type: 'advertisement',
                    Author: this.author
                };
            }
        }
    });
    return providers;
});


