define
([
    'jquery','jquery/superdesk', 'gizmo/superdesk/action'
],
function($, superdesk, Action)
{
    return { init: function() 
    {
        getScript = function(action){
            if(action.get('Path') == 'modules.user.list' && action.get('Script'))
                require([action.get('Script').href], function(app){ app(); });
        }

        Action.get('modules.user.list')
        .done(getScript);
    }};
});