<<<<<<< HEAD
define(['gizmo/superdesk', 
        /*'livedesk/models/blog-admin',
        'livedesk/models/blog-collaborator',
        'livedesk/models/user',
        'livedesk/models/language',
        'livedesk/models/post'*/], 
function(Gizmo)
=======
define([ 'gizmo/superdesk', 
    config.guiJs('livedesk', 'models/user'),
    config.guiJs('livedesk', 'models/language'),
    config.guiJs('livedesk', 'models/posts'),
    config.guiJs('livedesk', 'models/collaborators')],
    
function(giz, User, Language, Posts, Collaborators)
>>>>>>> 53661705f0bbc7f580a53732373fba4de3a4df4d
{
    // Blog
    return Gizmo.AuthModel.extend
    ({
		url: new Gizmo.Url('Blog'),/*
        defaults:
        { 
            Creator: User,
            Language: Language,
<<<<<<< HEAD
            Post:               Gizmo.Collection.extend({ model: Gizmo.Model.Post }),
            PostPublished:      Gizmo.Collection.extend({ model: Gizmo.Model.Post }),
            PostUnpublished:    Gizmo.Collection.extend({ model: Gizmo.Model.Post })
        }*/
    }, { register: 'Blog' } );
=======
            Collaborator: Collaborators,
            Post: Posts,
            PostPublished: Posts,
            PostUnpublished: Posts
        }
    }, 
    { register: 'Blog' } );
>>>>>>> 53661705f0bbc7f580a53732373fba4de3a4df4d
});