define([
    'jquery',
    'backbone',
    'jquery/superdesk',
    'gizmo/superdesk/action',
    'jquery/tmpl',
    'tmpl!livedesk>error-notif'
], 
function($, Backbone, superdesk, Action) 
{
    return Backbone.Router.extend
    ({
        routes: 
        {
            'desks/task/:action': 'taskAction'
        },
        taskAction: function(action)
        {
            Action.initApp('modules.desks.tasks.'+action);
        }
    });
});