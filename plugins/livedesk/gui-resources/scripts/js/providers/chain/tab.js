define(['providers'], function(providers) 
{
    providers.chain = 
    {
        className: 'big-icon-chain',       
        tooltip: _('Liveblogs'),
        init: function() 
        {
            var args = arguments;
            require(['providers','providers/chain'], 
                function(providers){ 
                    providers.chain.init.apply(providers.chain, args); 
                    $("[rel=tooltip]").tooltip();
                });
        }
    };
    return providers;
});