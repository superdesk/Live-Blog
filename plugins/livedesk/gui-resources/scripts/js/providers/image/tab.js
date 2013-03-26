define('providers/image/tab', 
['providers', 'providers/_utils'], 
function(providers, utils) 
{
    providers.image =
    {
        className: 'big-icon-instagram',    
        tooltip: _('Images'),
        init: function() 
        {
            var args = arguments;
            require(['providers','providers/image'], 
                function(providers){ providers.image.init.apply(providers.image, args); });
        }
    };
    return providers;
});