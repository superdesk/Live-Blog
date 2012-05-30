define('providers/twitter/adaptor', [
    'providers', 'jquery'
], function(providers, $)
{
    $.extend(providers.ads, 
    {
        adaptor: {
            universal: function(obj) 
            {
                return parseInt($(obj).attr('data-post-id'));
            }
        }
    });
    return providers;
});


