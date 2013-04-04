define
([
    'jquery',
    'gizmo/superdesk',
    'gizmo/superdesk/action',
    'tmpl!superdesk/desks>singledesk',
], 
function($, giz, Action)
{    
    
    return { init: function(){ Action.initApp('modules.desks.tasks.add'); }}; 
    
});