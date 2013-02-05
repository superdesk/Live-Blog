define([ 'gizmo/superdesk', 
    config.guiJs('livedesk', 'models/blog-collaborator-type')
],
function( Gizmo ) 
{
    // LiveBlogs
    return Gizmo.Collection.extend
    ({
		url: new Gizmo.Url('LiveDesk/BlogCollaboratorType/'),
        model: Gizmo.Register.BlogCollaaboratorType
    }, { register: 'BlogCollaaboratorTypes' } );
});