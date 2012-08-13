define(['jquery', 'jquery/superdesk'], function($, superdesk)
{
    var loadMediaArchive = function(action)
    {
        action.ScriptPath && 
            require([superdesk.apiUrl+action.ScriptPath], function(App){ App(); });
    };
    
    return { init: function()
    { 
        superdesk.getAction('modules.media-archive.main').done(loadMediaArchive);
    }};
});