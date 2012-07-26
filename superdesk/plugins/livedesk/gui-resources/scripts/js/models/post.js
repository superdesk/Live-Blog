define([ 'gizmo/superdesk'],
function(Gizmo)
{
    // Post
	return Gizmo.AuthModel.extend({
		url: new Gizmo.Url('/Post')
	}, { register: 'Post' } );
	/*
    return Gizmo.AuthModel.extend
    ({ 
		url: new Gizmo.Url('/Post'),
		defaults:
        { 
            Author: Collaborator,
            Blog: Blog,
            Creator: User,
            PostType: PostType
        }
    }, { register: 'Post' } );*/
});