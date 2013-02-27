define([ 'gizmo/superdesk',
    config.guiJs('livedesk', 'models/blog'),
    config.guiJs('livedesk', 'models/post'),
    config.guiJs('superdesk/user', 'models/person-meta')],
function(Gizmo, Blog, Post, PersonMeta)
{
    // User
    return Gizmo.Model.extend
    ({ 
        defaults:
        { 
            Blog: Gizmo.Collection.extend(Blog),
            Post: Gizmo.Collection.extend(Post),
            MetaData: PersonMeta
        }
    }, { register: 'User' } );
});