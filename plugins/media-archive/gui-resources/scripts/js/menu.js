define
([
    'jquery','jquery/superdesk', 'gizmo/superdesk/action'
],
function($, superdesk, Action)
{
    return { init: function() 
    {
        Action.initApp('modules.media-archive.main');
        return;
        
        superdesk.getAction('modules.media-archive.main')
        .done(function(action)
        {
            if( !action ) return; 
            if( action.Path == 'modules.media-archive.main' && action.Script )
                require([action.Script.href], function(app){ app(); });
        });
    }};
});