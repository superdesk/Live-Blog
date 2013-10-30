define
([
    'jquery','jquery/superdesk', 'gizmo/superdesk/action'
],
function($, superdesk, Action)
{
    return { init: function() 
    {
        return Action.initApp('modules.media-archive.main');
    }};
});