define(['gizmo/superdesk', 
        'gui/superdesk/livedesk/scripts/js/models/collaborator',
        'gui/superdesk/livedesk/scripts/js/models/blog',
        'gui/superdesk/livedesk/scripts/js/models/user',
        'gui/superdesk/livedesk/scripts/js/models/post-type'], 
function(giz, Collaborator, Blog, User, PostType)
{
    // Post
    return giz.Model.extend
    ({ 
        defaults:
        { 
            Author: Collaborator,
            Blog: Blog,
            Creator: User,
            PostType: PostType
        }
    });
});