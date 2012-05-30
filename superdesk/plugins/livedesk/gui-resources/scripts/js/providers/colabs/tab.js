define('providers/colabs/tab', ['providers'], 
function(providers) 
{
    providers.colabs = 
    {
        className: 'big-icon-collaborators',       
        init: function() 
        {
            var args = arguments;
            require(['providers','providers/colabs'], 
                function(providers){ providers.colabs.init.apply(providers.colabs, args); });
        }
    };
    return providers;
});