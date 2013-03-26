define(['providers'], function(providers) 
{
    providers.liveblog = 
    {
        className: 'big-icon-chain',       
        tooltip: _('Liveblogs'),
        init: function() 
        {
            var args = arguments;
            require(['providers','providers/liveblog'], 
                function(providers){ 
                    providers.liveblog.init.apply(providers.liveblog, args); 
                    $("[rel=tooltip]").tooltip();
                });
        }
    };
    return providers;
});