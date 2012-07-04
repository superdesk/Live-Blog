define([ 'gizmo',
         'gui/superdesk/livedesk/scripts/js/models/post',
         'gui/superdesk/livedesk/scripts/js/models/blog' ], 
function(giz, Post, Blog)
{
    // User
    return giz.Model.extend
    ({ 
        defaults:
        { 
            Blog: new giz.Collection(Blog),
            BlogAdmin: new giz.Collection(Blog),
            Post: new giz.Collection(Post),
            PostPublished: new giz.Collection(Post),
            PostUnpublished: new giz.Collection(Post)
        }
    });
});