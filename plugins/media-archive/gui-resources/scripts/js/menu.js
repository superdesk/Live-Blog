define
([
    'jquery','jquery/superdesk',
],
function($, superdesk)
{
    return { init: function() 
    {
        superdesk.getAction('modules.media-archive.main')
        .done(function(action)
        {
            if( !action ) return; 
            if( action.Path == 'modules.media-archive.main' && action.ScriptPath )
                require([superdesk.apiUrl+action.ScriptPath], function(app){ app(); });
        });
    }};
});