define(['gizmo/superdesk', 
        'livedesk/models/collaborator'], 
function(Gizmo)
{
    return Gizmo.Collection.extend({ 
		model: Gizmo.Model.Collaborator 
	}, { register: 'Collaborators' } );
});