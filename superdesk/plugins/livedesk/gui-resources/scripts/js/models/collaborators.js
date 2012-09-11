define(['gizmo/superdesk', config.guiJs('livedesk', 'models/collaborator')], 
function(giz, Collaborator)
{
    return giz.Collection.extend({ model: Collaborator }, { register: 'Collaborators' } );
});