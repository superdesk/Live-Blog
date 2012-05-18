var providerName = 'colabs';

define('providers/'+providerName+'/tab', ['providers'], 
function(providers) 
{
    providers[providerName] = 
    {
        className: 'big-icon-collaborators',       
        init: function() 
        {
            var args = arguments;
            require(['providers','providers/'+providerName], 
                function(providers){ providers[providerName].init.apply(providers[providerName], args); });
        }
    };
    return providers;
});