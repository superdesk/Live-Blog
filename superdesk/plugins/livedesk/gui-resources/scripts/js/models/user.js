define([ 'gizmo/superdesk',
    config.guiJs('livedesk', 'models/blog') ],
function(Gizmo, Blog, Post)
{
    // User
    return Gizmo.Model.extend
    ({ 
        defaults:
        { 
            Blog: Gizmo.Collection.extend(Blog),
            Post: Gizmo.Collection.extend(Post)
        }
    });
});