define
([ 
    
    'jquery',
    'gizmo/superdesk/action',
    'gizmo/superdesk/models/actions'
 ], 
function($, Action, Actions) 
{
    var newActions = new Actions();
    return $.extend(true, Action, {actions: newActions});
});