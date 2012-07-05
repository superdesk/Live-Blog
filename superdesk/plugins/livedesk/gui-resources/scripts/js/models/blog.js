define(['gizmo/superdesk', 
        'gui/superdesk/livedesk/scripts/js/models/blog-admin',
        'gui/superdesk/livedesk/scripts/js/models/blog-collaborator',
        'gui/superdesk/livedesk/scripts/js/models/user',
        'gui/superdesk/livedesk/scripts/js/models/language',
        'gui/superdesk/livedesk/scripts/js/models/post'], 
function(giz, Admin, Collaborators, User, Language, Post)
{
    // Blog
    return giz.Model.extend
    ({ 
        defaults:
        { 
            Admin: Admin,
            Collaborator: Collaborators,
            Creator: User,
            Language: Language,
            Post:               giz.Collection.extend({ model: Post }),
            PostPublished:      giz.Collection.extend({ model: Post }),
            PostUnpublished:    giz.Collection.extend({ model: Post })
        }
    });
});