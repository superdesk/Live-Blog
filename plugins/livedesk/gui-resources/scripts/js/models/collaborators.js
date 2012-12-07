define(['gizmo/superdesk', config.guiJs('livedesk', 'models/collaborator')], 
function(Gizmo, Collaborator)
{
    return Gizmo.Collection.extend({ 
    	url: new Gizmo.Url('Superdesk/Collaborator'),
    	model: Collaborator
    }, { register: 'Collaborators' } );
});