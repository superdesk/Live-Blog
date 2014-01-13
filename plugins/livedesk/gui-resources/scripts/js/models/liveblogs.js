define([ 'gizmo/superdesk', 
    config.guiJs('livedesk', 'models/blog')
],
function( Gizmo ) 
{
    // LiveBlogs
    return Gizmo.Collection.extend
    ({
		url: new Gizmo.Url('LiveDesk/Blog/Live'),
        model: Gizmo.Register.Blog
    }, { register: 'LiveBlogs' } );
});