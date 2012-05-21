var providerName = 'colabs';
define( 'providers/'+providerName+'/adaptor', 
['providers', 'jquery', 'jquery/rest','jquery/utils', 'providers/'+providerName+'/tab'], 
function(providers)
{
    $.extend( providers[providerName], 
    {
        adaptor: 
        {
            init: function() 
            {
                var self = this;
                new $.rest('Superdesk/Collaborator/')
                    .xfilter('Id')
                    .request({data: { name: 'google'}})
                    .done(function(collabs)
                    {
                        if($.isDefined(collabs[0])) {
                            self.author = collabs[0].Id;
                        }
                    });
                //new $.restAuth(theBlog)
            },
            web: function(obj) 
            {
                return { Content: $(obj).find('p.result-text').html(), 
                    Type: $(obj).attr('data-post-type') || 'normal',
                    Author: $(obj).attr('data-colab-id') };
            }
        }
    });
    return providers;
});