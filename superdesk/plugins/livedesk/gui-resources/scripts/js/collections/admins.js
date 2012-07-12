define(['gizmo/superdesk', 
        'gui/superdesk/livedesk/scripts/js/models/admin'], 
function(giz, Admin)
{
    // Blog Admin list
    return giz.Collection.extend({ model: Admin });
});