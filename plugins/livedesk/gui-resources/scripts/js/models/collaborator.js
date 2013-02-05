define(['gizmo/superdesk',
    config.guiJs('livedesk', 'models/posts'),
    config.guiJs('livedesk', 'models/source'),
    config.guiJs('livedesk', 'models/person'),
    config.guiJs('livedesk', 'models/user')],
function( Gizmo ) {
    // Collaborator
    return Gizmo.Model.extend
    ({ 
        defaults:
        { 
            Post: Gizmo.Register.Posts,
            PostPublished: Gizmo.Register.Posts,
            PostUnpublished: Gizmo.Register.Posts,
            Source: Gizmo.Register.Source,
            Person: Gizmo.Register.Person,
            User: Gizmo.Register.User
        },
        saveType: function(type) {
            var typeHref = this.href+'/Type/'+type;
            var
                self = this,
                dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); },
                ret = dataAdapter(typeHref).update();
            return ret;
        },
    }, { register: 'Collaborator' } );
});