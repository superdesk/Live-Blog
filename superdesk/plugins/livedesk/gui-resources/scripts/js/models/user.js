define([ 'gizmo',
         'livedesk/models/post',
         'livedesk/models/blog' ], 
function(Gizmo, Post, Blog)
{
    // User
    return Gizmo.Model.extend
    ({ 
        defaults:
        { 
            Blog: new Gizmo.Collection(Gizmo.Model.Blog),
            BlogAdmin: new Gizmo.Collection(Gizmo.Model.Blog),
            Post: new Gizmo.Collection(Gizmo.Model.Post),
            PostPublished: new Gizmo.Collection(Gizmo.Model.Post),
            PostUnpublished: new Gizmo.Collection(Gizmo.Model.Post)
        }
    });
});