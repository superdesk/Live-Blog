define(['gizmo/superdesk', 
        'gui/superdesk/livedesk/scripts/js/models/blog-admin',
        'gui/superdesk/livedesk/scripts/js/models/blog-collaborator',
        'gui/superdesk/livedesk/scripts/js/models/user',
        'gui/superdesk/livedesk/scripts/js/models/language',
        'gui/superdesk/livedesk/scripts/js/models/post'], 
function(giz, Admin, Collaborator, User, Language, Post)
{
    // Blog
    return giz.Model.extend
    ({ 
        defaults:
        { 
            Admin: Admin,
            Collaborator: Collaborator,
            Creator: User,
            Language: Language,
            Post: new giz.Collection(Post),
            PostPublished: new giz.Collection(Post),
            PostUnpublished: new giz.Collection(Post)
        }
    });
});