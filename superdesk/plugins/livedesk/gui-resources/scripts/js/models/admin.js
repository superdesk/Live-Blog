define(['gizmo/superdesk', 
        'gui/superdesk/livedesk/scripts/js/models/blog'], 
function(giz, Blog)
{
    // Admin
    return giz.Model.extend
    ({ 
        defaults:
        { 
            Blog: Blog
        }
    });
});