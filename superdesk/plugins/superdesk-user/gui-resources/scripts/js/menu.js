define
([
    'jquery','jquery/superdesk',
],
function($, superdesk)
{
    superdesk.getAction('modules.user.list')
    .done(function(action)
    {
        var callback = function()
        { 
            require([superdesk.apiUrl+action.ScriptPath], function(app){ app(); }); 
        };
        action.ScriptPath && superdesk.navigation.bind( $(self).attr('href')||'users', callback, $(self).text()||'Users' );
    });
});