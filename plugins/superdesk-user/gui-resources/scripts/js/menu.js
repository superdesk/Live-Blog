define
([
    'jquery','jquery/superdesk',
],
function($, superdesk)
{
    return { init: function() 
    {
        superdesk.getAction('modules.user.list')
        .done(function(action)
        {
            if(action.Path == 'modules.user.list' && action.Script)
                require([action.Script.href], function(app){ app(); });
        });
    }};
});