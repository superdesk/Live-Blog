define
([
    'jquery',
    'gizmo/superdesk',
    'gizmo/superdesk/action',
    config.guiJs('superdesk/desks', 'router')
    //'tmpl!superdesk/desks>singledesk',
], 
function($, giz, Action, router)
{    
    new router;
    
    //return { init: function(){ Action.initApp('modules.desks.tasks.add'); }}; 
    return { init: function(){ Action.initApp('modules.desks.single'); }}; 
});