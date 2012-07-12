define(['gizmo/superdesk', 
        'livedesk/models/blog-admin',
        'livedesk/models/blog-collaborator',
        'livedesk/models/user',
        'livedesk/models/language',
        'livedesk/models/post'], 
function(Gizmo)
{
    // Blog
    return giz.Model.extend
    ({ 
        defaults:
        { 
            Admin: Gizmo.Model.Admin,
            Collaborator: Collaborators,
            Creator: User,
            Language: Language,
            Post:               Gizmo.Collection.extend({ model: Gizmo.Model.Post }),
            PostPublished:      Gizmo.Collection.extend({ model: Gizmo.Model.Post }),
            PostUnpublished:    Gizmo.Collection.extend({ model: Gizmo.Model.Post })
        }
    }, { register: 'Blog' } );
});