define(['gizmo/superdesk',
    config.guiJs('livedesk', 'models/posts'),
    config.guiJs('livedesk', 'models/unpublishedposts'),
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
            PublishedPost: Gizmo.Register.Posts,
            UnpublishedPost: Gizmo.Register.UnpublishedPosts,
            Source: Gizmo.Register.Source,
            Person: Gizmo.Register.Person,
            User: Gizmo.Register.User
        },
        saveType: function(type, href) {
            var typeHref = href+this.get('Id')+'/Type/'+type,
                self = this,
                dataAdapter = function(){ return self.syncAdapter.request.apply(self.syncAdapter, arguments); },
                ret = dataAdapter(typeHref).update();
            return ret;
        },
    }, { register: 'Collaborator' } );
});