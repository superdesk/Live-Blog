define([ 'jquery','jquery/superdesk', 'gizmo/superdesk/action', 'router' ],
function($, superdesk, Action, router)
{
    return { init: function() 
    {
        Action.get('modules.article.list')
        .done(function(action)
        {
            if(action.get('Path') == 'modules.article.list' && action.get('Script'))
                require([action.get('Script').href], function(app){ app(); });
        });
    }};
});