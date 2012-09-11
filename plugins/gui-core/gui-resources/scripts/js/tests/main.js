requirejs.config
({ 
    paths: 
    {
        'qunit': 'qunit',
        'unit': 'unit'
    }
});

require(['unit/gizmo'], 
function($)
{
    for( var i in arguments ) try
    {
        arguments[i].run();
    }
    catch(e){ console.error(e); };
});
