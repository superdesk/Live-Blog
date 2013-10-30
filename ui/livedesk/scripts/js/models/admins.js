define(['gizmo/superdesk', 
        config.guiJs('livedesk', 'models/admin')], 
function(giz, Admin)
{
    // Blog Admin list
    return giz.Collection.extend({ model: Admin });
});