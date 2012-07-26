define([ 'gizmo/superdesk', 
/*    config.guiJs('livedesk', 'models/user'),
    config.guiJs('livedesk', 'models/language'),
    config.guiJs('livedesk', 'models/posts'),
    config.guiJs('livedesk', 'models/collaborators')*/],
    
function(Gizmo, User, Language, Posts, Collaborators) {
    // Blog
    return Gizmo.AuthModel.extend
    ({
		url: new Gizmo.Url('Blog'),
/*        defaults:
        { 
            Creator: User,
            Language: Language,
            Collaborator: Collaborators,
            Post: Posts,
            PostPublished: Posts,
            PostUnpublished: Posts
        }
*/		
    }, 
    { register: 'Blog' } );
});