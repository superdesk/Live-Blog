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
        url: new Gizmo.Url('Data/Collaborator')
    }, { register: 'NewCollaborator' } );
});