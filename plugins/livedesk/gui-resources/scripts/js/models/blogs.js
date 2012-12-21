define([ 'gizmo/superdesk', 
    config.guiJs('livedesk', 'models/blog')
],
function( Gizmo ) 
{
    // Blogs
    return Gizmo.Collection.extend
    ({
		url: new Gizmo.Url('LiveDesk/Blog'),
        model: Gizmo.Register.Blog
    }, { register: 'Blogs' } );
});