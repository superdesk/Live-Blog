define(['gizmo/superdesk', 
        'livedesk/models/blog'], 
function(Gizmo)
{
    return Gizmo.Model.extend
    ({ 
        defaults:
        { 
            Blog: Gizmo.Model.Blog
        }
    }, { register: 'Admin' } );
});