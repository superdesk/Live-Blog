define(['gizmo/superdesk', 
		'livedesk/models/post'], 
function(Gizmo)
{
    return new Gizmo.Collection(Gizmo.Model.Post);
});