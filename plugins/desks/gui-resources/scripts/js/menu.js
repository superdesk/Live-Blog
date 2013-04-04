define([ 'jquery','jquery/superdesk', 'gizmo/superdesk/action' ],
function($, superdesk, Action)
{
    return { init: function() 
    {
        Action.initApp('modules.desks.main');
    }};
});