var providerName = 'colabs';
define( 'providers/'+providerName+'/adaptor', 
['providers', 'jquery', 'jquery/rest','jquery/utils', 'providers/'+providerName+'/tab'], 
function(providers)
{
    $.extend( providers[providerName], 
    {
        adaptor: 
        {
            universal: function(obj)
            {
               return parseInt($(obj).attr('data-post-id'));
            }
        }
    });
    return providers;
});